"""验证直接财报入口的缺口处理、证据保留和无会话执行。"""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import read_financial_statements as financial
from read_financial_statements import JsonValue


def receipt() -> dict[str, JsonValue]:
    """构造可追溯报表。参数：无。返回：测试凭据。异常：无。"""
    return {'accessed_at': '2026-11-04T10:00:00+00:00',
            'snapshot': {'source_hash': 'source-1', 'processed_hash': 'parsed-1'},
            'result': {'currency': 'CNY', 'units': 'CNY', 'scale': 'millions',
                       'periods': [{'period_start': '2026-01-01', 'period_end': '2026-06-30'}],
                       'rows': [{'label': '归母净利润', 'values': [0], 'page_no': 9, 'source_table_ref': 't3'}]}}


class Reader:
    """只提供财报端口，故意不具备研究会话能力。"""

    def __init__(self) -> None:
        """初始化凭据。参数：无。返回：无。异常：无。"""
        self.prepares: list[tuple[str, str]] = []
        self.reads: list[str | None] = []
        self.receipts: dict[str, dict[str, JsonValue]] = {kind: receipt() for kind in financial.STATEMENTS}
        self.table: dict[str, JsonValue] = {'result': {'data': {'rows': [['附注', '100']]}, 'table_ref': 't7'}}

    def prepare(self, ticker: str, document_id: str, token: None) -> dict[str, JsonValue]:
        """记录准备。参数：标的、文档、令牌。返回：缓存状态。异常：无。"""
        self.prepares.append((ticker, document_id))
        return {'processed': True, 'cached': True}

    def read(self, ticker: str, document_id: str, *, statement_type: str | None,
             table_ref: str | None, token: None) -> dict[str, JsonValue]:
        """返回报表或附注。参数：标的、文档、类型或原表、令牌。返回：凭据。异常：未知类型。"""
        self.reads.append(statement_type)
        return self.receipts[statement_type] if statement_type is not None else self.table


class Catalog:
    """最小财报索引。"""

    def list_documents(self, *, ticker: str) -> dict[str, JsonValue]:
        """列出实际ID。参数：标的。返回：来源索引。异常：无。"""
        return {'documents': [{'document_id': 'fil-1', 'fiscal_year': 2026, 'ticker': ticker}]}

    def list_tables(self, *, ticker: str, document_id: str) -> dict[str, JsonValue]:
        """提供真实原表引用。参数：标的、文档。返回：表索引。异常：无。"""
        return {'tables': [{'table_ref': 't7', 'page_no': 9}]}


class FinancialStatementsTests(unittest.TestCase):
    """测试数值、缺口与命令的真实结果。"""

    def test_zero_is_a_value_and_original_evidence_survives(self) -> None:
        """零值与原件定位不丢失。参数：无。返回：无。异常：断言失败。"""
        reader = Reader()
        result = financial.extract(reader, '600036', 'fil-1', financial.STATEMENTS)
        self.assertEqual(result['status'], 'extracted')
        self.assertEqual(reader.prepares, [('600036', 'fil-1')])
        self.assertEqual(reader.reads, list(financial.STATEMENTS))
        statements = result['statements']
        assert isinstance(statements, dict)
        income = statements['income']
        assert isinstance(income, dict)
        self.assertEqual(income['receipt'], reader.receipts['income'])
        self.assertEqual(income['numeric_cells'], 1)

    def test_missing_currency_and_number_units_remain_partial(self) -> None:
        """不猜测QS式缺失口径。参数：无。返回：无。异常：断言失败。"""
        r = receipt()
        raw = r['result']
        assert isinstance(raw, dict)
        raw.update(currency=None, units='NUMBER')
        result = financial.assess_statement(r)
        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['issues'], ['missing_currency', 'missing_or_unknown_units'])
        self.assertIsNone(raw['currency'])

    def test_blank_values_and_booleans_are_not_financial_amounts(self) -> None:
        """空值和布尔值不构成覆盖。参数：无。返回：无。异常：断言失败。"""
        for values in [[None], [True], []]:
            r = receipt()
            raw = r['result']
            assert isinstance(raw, dict)
            raw['rows'] = [{'values': values}]
            self.assertIn('no_numeric_cells', financial.assess_statement(r)['issues'])

    def test_period_alignment_and_invalid_dates_are_reported(self) -> None:
        """期间与金额必须对齐。参数：无。返回：无。异常：断言失败。"""
        r = receipt()
        raw = r['result']
        assert isinstance(raw, dict)
        raw['periods'] = [{'period_end': '2026-02-30'}, {'period_end': '2025-06-30'}]
        result = financial.assess_statement(r)
        self.assertIn('invalid_period_end', result['issues'])
        self.assertIn('period_value_count_mismatch', result['issues'])

    def test_missing_periods_and_nonfinite_amounts_fail_basic_checks(self) -> None:
        """空期间与非有限值保留缺口。参数：无。返回：无。异常：断言失败。"""
        r = receipt()
        raw = r['result']
        assert isinstance(raw, dict)
        raw['periods'] = []
        raw['rows'] = [{'values': [float('nan')]}]
        result = financial.assess_statement(r)
        for issue in ['missing_periods', 'nonfinite_amount', 'no_numeric_cells']:
            self.assertIn(issue, result['issues'])

    def test_unsupported_statement_is_not_promoted_to_success(self) -> None:
        """后端降级与缺结果均不能成功。参数：无。返回：无。异常：断言失败。"""
        for r in [{}, {'result': {'supported': False}}, {'result': {'data_quality': 'unavailable'}}]:
            self.assertEqual(financial.assess_statement(r)['status'], 'unavailable')

    def test_cli_persists_complete_receipt_but_prints_small_summary(self) -> None:
        """完整JSON落盘且无研究系统依赖。参数：无。返回：无。异常：断言失败。"""
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'nested/statements.json'
            stream = io.StringIO()
            with patch.object(financial, 'build_backend', return_value=(Reader(), Catalog())), redirect_stdout(stream):
                code = financial.main(['--workspace', tmp, '--output', str(output), 'extract', '--ticker', 'META', '--document-id', 'fil-1'])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(stream.getvalue())['status'], 'extracted')
            self.assertIn('source_hash', output.read_text())
            self.assertFalse((Path(tmp) / '.alpha/research').exists())

    def test_partial_exit_code_keeps_all_three_receipts(self) -> None:
        """缺一张表时仍保留其他表。参数：无。返回：无。异常：断言失败。"""
        reader = Reader()
        reader.receipts['income'] = {'result': {'supported': False}}
        stream = io.StringIO()
        with patch.object(financial, 'build_backend', return_value=(reader, Catalog())), redirect_stdout(stream):
            code = financial.main(['--workspace', '.', 'extract', '--ticker', 'QS', '--document-id', 'fil-1'])
        self.assertEqual(code, 2)
        self.assertEqual(len(json.loads(stream.getvalue())['statements']), 3)

    def test_list_retains_document_ids_and_table_is_not_a_statement(self) -> None:
        """索引和附注不冒充标准三表。参数：无。返回：无。异常：断言失败。"""
        with patch.object(financial, 'build_backend', return_value=(Reader(), Catalog())):
            stream = io.StringIO()
            with redirect_stdout(stream):
                code = financial.main(['--workspace', '.', 'list', '--ticker', 'META'])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(stream.getvalue())['catalog']['documents'][0]['document_id'], 'fil-1')
            stream = io.StringIO()
            with redirect_stdout(stream):
                code = financial.main(['--workspace', '.', 'table', '--ticker', 'META', '--document-id', 'fil-1', '--table-ref', 't7'])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(stream.getvalue())['status'], 'table_read')
            self.assertNotIn('statements', json.loads(stream.getvalue()))

    def test_tables_discovery_and_unsupported_table_preserve_gap(self) -> None:
        """表引用从本文件发现，不能猜测。参数：无。返回：无。异常：断言失败。"""
        reader = Reader()
        with patch.object(financial, 'build_backend', return_value=(reader, Catalog())):
            stream = io.StringIO()
            with redirect_stdout(stream):
                code = financial.main(['--workspace', '.', 'tables', '--ticker', 'META', '--document-id', 'fil-1'])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(stream.getvalue())['catalog']['tables'][0]['table_ref'], 't7')
            reader.table = {'result': {'supported': False, 'error': {'code': 'not_supported'}}}
            stream = io.StringIO()
            with redirect_stdout(stream):
                code = financial.main(['--workspace', '.', 'table', '--ticker', 'META', '--document-id', 'fil-1', '--table-ref', 't7'])
            self.assertEqual(code, 2)
            self.assertFalse(json.loads(stream.getvalue())['receipt']['result']['supported'])

    def test_missing_backend_returns_explicit_error_without_installing(self) -> None:
        """依赖缺失不安装也不伪造数据。参数：无。返回：无。异常：断言失败。"""
        stream = io.StringIO()
        with patch.object(financial, 'build_backend', side_effect=ImportError('alpha is not installed')), redirect_stderr(stream):
            code = financial.main(['--workspace', '.', 'list', '--ticker', 'META'])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(stream.getvalue())['error_type'], 'ImportError')

    def test_backend_execution_error_is_not_a_financial_data_gap(self) -> None:
        """第三方异常与报表不支持分开。参数：无。返回：无。异常：断言失败。"""
        stream = io.StringIO()
        with patch.object(financial, 'build_backend', side_effect=KeyError('backend configuration')), redirect_stderr(stream):
            code = financial.main(['--workspace', '.', 'list', '--ticker', 'META'])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(stream.getvalue())['error_type'], 'KeyError')

    def test_help_works_without_site_packages_or_alpha(self) -> None:
        """帮助不加载可选解析后端。参数：无。返回：无。异常：断言失败。"""
        result = subprocess.run([sys.executable, '-I', '-S', str(SCRIPTS / 'read_financial_statements.py'), '--help'], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('extract', result.stdout)

    def test_invalid_workspace_fails_before_backend_loading(self) -> None:
        """不隐式初始化工作区。参数：无。返回：无。异常：断言失败。"""
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                financial.build_backend(Path(tmp) / 'absent')


if __name__ == '__main__':
    unittest.main()
