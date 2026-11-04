#!/usr/bin/env python3
"""直接提取Fins财报，不创建Alpha研究会话或调用模型。

财报后端是可选依赖；仅执行实际提取时加载，帮助和结果检查可独立运行。
原件与解析产物始终由Fins仓储访问；输出文件只是本次提取的证据副本。
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import json
import math
from pathlib import Path
import sys
from typing import Literal, NotRequired, Protocol, TypeAlias, TypedDict, cast

JsonValue: TypeAlias = str | int | float | bool | None | list['JsonValue'] | dict[str, 'JsonValue']
STATEMENTS = ('income', 'balance_sheet', 'cash_flow')
UNKNOWN_UNITS = frozenset({'NUMBER', 'UNKNOWN', 'N/A'})
SCHEMA_VERSION = 1
EXIT_PARTIAL = 2


class StatementAssessment(TypedDict):
    """最低读取条件及明确缺口，不承担经济解释。"""

    status: Literal['extracted', 'partial', 'unavailable']
    issues: list[str]
    numeric_cells: NotRequired[int]
    period_count: NotRequired[int]
    reason: NotRequired[JsonValue]


class FinancialReader(Protocol):
    """仅使用财报准备与带快照读取，不依赖研究状态。"""

    def prepare(self, ticker: str, document_id: str, token: None) -> dict[str, JsonValue]:
        """准备源文档。参数：标的、文档、空取消令牌。返回：处理摘要。异常：处理失败。"""
        ...

    def read(self, ticker: str, document_id: str, *, statement_type: str | None,
             table_ref: str | None, token: None) -> dict[str, JsonValue]:
        """读取财报。参数：标的、文档、三表或原表选择、令牌。返回：快照凭据。异常：读取失败。"""
        ...


class FinancialCatalog(Protocol):
    """财报文档索引端口。"""

    def list_documents(self, *, ticker: str) -> dict[str, JsonValue]:
        """列出文档。参数：标的。返回：带来源和期间的索引。异常：标的或仓储错误。"""
        ...

    def list_tables(self, *, ticker: str, document_id: str) -> dict[str, JsonValue]:
        """列出原表定位。参数：标的、文档。返回：表格引用索引。异常：文档或解析错误。"""
        ...


def build_backend(workspace: Path) -> tuple[FinancialReader, FinancialCatalog]:
    """装配可选后端。参数：已有工作区。返回：读取与索引端口。异常：依赖缺失或目录错误。"""
    if not workspace.is_dir():
        raise ValueError('workspace必须是已有目录；此脚本不初始化研究系统')
    # 可选后端只在实际使用时导入；不依赖alpha-research Skill或其Session/Host装配。
    from alpha.fins.research_reader import FinsResearchReader
    from alpha.fins.service_runtime import DefaultFinsRuntime

    runtime = DefaultFinsRuntime.create(workspace_root=workspace.resolve())
    return FinsResearchReader(runtime), cast(FinancialCatalog, runtime.get_tool_service())


def assess_statement(receipt: dict[str, JsonValue]) -> StatementAssessment:
    """检查最低读取条件。参数：原始凭据。返回：状态及缺口。异常：无。

    不推断货币、缩放或会计范围，不把数值存在视作原件核验完成。
    """
    raw = receipt.get('result')
    if not isinstance(raw, dict):
        return {'status': 'unavailable', 'issues': ['missing_statement_result']}
    if raw.get('supported') is False or raw.get('data_quality') == 'unavailable':
        return {'status': 'unavailable', 'issues': ['backend_unavailable'], 'reason': raw.get('reason', raw.get('error'))}
    issues: list[str] = []
    currency, units = raw.get('currency'), raw.get('units')
    if not isinstance(currency, str) or not currency.strip() or currency.strip().upper() in UNKNOWN_UNITS:
        issues.append('missing_currency')
    if not isinstance(units, str) or not units.strip() or units.strip().upper() in UNKNOWN_UNITS:
        issues.append('missing_or_unknown_units')
    periods = raw.get('periods')
    if not isinstance(periods, list) or not periods:
        issues.append('missing_periods')
        periods = []
    for period in periods:
        end = period.get('period_end') if isinstance(period, dict) else None
        try:
            if not isinstance(end, str):
                raise ValueError('missing period end')
            date.fromisoformat(end)
        except ValueError:
            issues.append('invalid_period_end')
            break
    numeric_cells = 0
    rows = raw.get('rows')
    if isinstance(rows, list):
        for row in rows:
            values = row.get('values') if isinstance(row, dict) else None
            if not isinstance(values, list):
                continue
            numbers = [v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
            numeric_cells += sum(math.isfinite(v) for v in numbers)
            if any(not math.isfinite(v) for v in numbers):
                issues.append('nonfinite_amount')
            if numbers and len(values) != len(periods):
                issues.append('period_value_count_mismatch')
    if not numeric_cells:
        issues.append('no_numeric_cells')
    return {'status': 'partial' if issues else 'extracted', 'issues': list(dict.fromkeys(issues)),
            'numeric_cells': numeric_cells, 'period_count': len(periods)}


def extract(reader: FinancialReader, ticker: str, document_id: str,
            statements: tuple[str, ...]) -> dict[str, JsonValue]:
    """准备并提取选定三表。参数：读取端口、标的、文档、类型。返回：原始凭据与逐表状态。异常：准备或读取失败。"""
    prepared = reader.prepare(ticker, document_id, None)
    results: dict[str, JsonValue] = {}
    for statement in statements:
        receipt = reader.read(ticker, document_id, statement_type=statement, table_ref=None, token=None)
        assessment = cast(dict[str, JsonValue], assess_statement(receipt))
        results[statement] = {**assessment, 'receipt': receipt}
    complete = all(isinstance(item, dict) and item['status'] == 'extracted' for item in results.values())
    return {'schema_version': SCHEMA_VERSION, 'provider': 'alpha.fins', 'operation': 'extract',
            'ticker': ticker, 'document_id': document_id, 'status': 'extracted' if complete else 'partial',
            'prepared': prepared, 'statements': results,
            'limitation': '仅检查数值、期间、币种和单位；合并范围、累计/单季、缩放及关键行仍须核对原表。不是Alpha研究验收或投资结论。'}


def parser() -> argparse.ArgumentParser:
    """建立命令入口。参数：无。返回：参数解析器。异常：无。"""
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument('--workspace', required=True, type=Path, help='已有Fins工作区，不需要研究session')
    result.add_argument('--output', type=Path, help='完整JSON副本；指定后stdout仅输出摘要')
    commands = result.add_subparsers(dest='command', required=True)
    for name in ('list', 'extract', 'tables', 'table'):
        command = commands.add_parser(name)
        command.add_argument('--ticker', required=True)
        if name != 'list':
            command.add_argument('--document-id', required=True)
        if name == 'extract':
            command.add_argument('--statement', nargs='+', choices=STATEMENTS, default=list(STATEMENTS))
        if name == 'table':
            command.add_argument('--table-ref', required=True)
    return result


def main(argv: list[str] | None = None) -> int:
    """运行一次提取。参数：命令行参数。返回：0成功、2缺口、1执行错误。异常：参数非法时argparse退出。"""
    args = parser().parse_args(argv)
    try:
        reader, catalog = build_backend(Path(args.workspace))
        ticker = str(args.ticker)
        if args.command == 'extract':
            value = extract(reader, ticker, str(args.document_id), tuple(args.statement))
        elif args.command == 'list':
            value = {'schema_version': SCHEMA_VERSION, 'provider': 'alpha.fins', 'operation': 'list',
                     'ticker': ticker, 'status': 'listed', 'catalog': catalog.list_documents(ticker=ticker)}
        elif args.command == 'tables':
            document_id = str(args.document_id)
            reader.prepare(ticker, document_id, None)
            value = {'schema_version': SCHEMA_VERSION, 'provider': 'alpha.fins', 'operation': 'tables',
                     'ticker': ticker, 'document_id': document_id, 'status': 'listed',
                     'catalog': catalog.list_tables(ticker=ticker, document_id=document_id)}
        else:
            document_id = str(args.document_id)
            reader.prepare(ticker, document_id, None)
            receipt = reader.read(ticker, document_id, statement_type=None, table_ref=str(args.table_ref), token=None)
            raw = receipt.get('result')
            supported = isinstance(raw, dict) and raw.get('supported') is not False
            value = {'schema_version': SCHEMA_VERSION, 'provider': 'alpha.fins', 'operation': 'table',
                     'ticker': ticker, 'document_id': document_id, 'status': 'table_read' if supported else 'partial',
                     'receipt': receipt, 'limitation': '原表读取不构成标准三表覆盖，金额和口径须核对。'}
        value['exported_at'] = datetime.now(timezone.utc).isoformat()
        encoded = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)
        if args.output is not None:
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(encoded, encoding='utf-8')
            print(json.dumps({'status': value['status'], 'output': str(output.resolve())}, ensure_ascii=False))
        else:
            print(encoded)
        return EXIT_PARTIAL if value['status'] == 'partial' else 0
    except Exception as error:
        # CLI是可选第三方后端的错误边界；异常只表示执行失败，不转换成无披露或成功。
        print(json.dumps({'status': 'error', 'error_type': type(error).__name__, 'reason': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
