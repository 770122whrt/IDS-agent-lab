"""
IDS XML Merger

合并多个 IDS XML 文件为一个完整的 IDS 文件。

核心功能:
1. 从多个 IDS 文件提取 specification 元素
2. 处理元数据（保留原始头信息或用户指定）
3. 检查 IFC 版本一致性
4. XSD 校验合并结果

作者: IDS-Agent
版本: 1.0.0
"""

import json
import logging
import copy
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from lxml import etree

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("IDSMerger")


# =============================================================================
# 命名空间定义
# =============================================================================

NAMESPACES = {
    'ids': 'http://standards.buildingsmart.org/IDS',
    'xs': 'http://www.w3.org/2001/XMLSchema',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
}

NSMAP = {
    'ids': NAMESPACES['ids'],
    'xs': NAMESPACES['xs'],
    'xsi': NAMESPACES['xsi'],
}


# =============================================================================
# 自定义异常
# =============================================================================

class IDSMergeError(Exception):
    """IDS 合并错误基类"""
    pass


class IFCVersionConflictError(IDSMergeError):
    """IFC 版本冲突错误"""

    def __init__(self, versions: Dict[str, List[str]]):
        self.versions = versions
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        lines = ["IFC version conflict detected:"]
        for version, specs in self.versions.items():
            lines.append(f"  - {version}: {len(specs)} specifications")
            for spec in specs[:3]:
                lines.append(f"      • {spec}")
            if len(specs) > 3:
                lines.append(f"      ... and {len(specs) - 3} more")
        return "\n".join(lines)


class XSDMergeValidationError(IDSMergeError):
    """XSD 校验失败错误"""

    def __init__(self, message: str, errors: list):
        self.message = message
        self.errors = errors
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        error_details = "\n".join([
            f"  - Line {e.line}: {e.message}" if hasattr(e, 'line') else f"  - {e}"
            for e in self.errors
        ])
        return f"{self.message}\n\nXSD Validation Errors:\n{error_details}"


# =============================================================================
# IDS 合并器
# =============================================================================

class IDSMerger:
    """
    合并多个 IDS XML 文件

    支持:
    - 提取并保留原始元数据
    - IFC 版本一致性检查
    - XSD Schema 校验
    - 多种版本冲突处理策略
    """

    def __init__(self, xsd_path: Optional[str] = None):
        """
        初始化合并器

        Args:
            xsd_path: XSD Schema 文件路径，默认为当前目录下的 ids.xsd
        """
        if xsd_path is None:
            xsd_path = Path(__file__).parent / "ids.xsd"
        self.xsd_path = Path(xsd_path)
        self._schema = None

    def _load_schema(self) -> etree.XMLSchema:
        """加载并缓存 XSD Schema"""
        if self._schema is None:
            if not self.xsd_path.exists():
                raise FileNotFoundError(f"XSD Schema file not found: {self.xsd_path}")

            with open(self.xsd_path, 'rb') as f:
                schema_doc = etree.parse(f)

            self._schema = etree.XMLSchema(schema_doc)

        return self._schema

    def merge(
        self,
        ids_files: List[str],
        output_path: str,
        info: Optional[Dict[str, str]] = None,
        on_version_conflict: str = "ask",
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        合并多个 IDS 文件

        Args:
            ids_files: IDS 文件路径列表
            output_path: 输出文件路径
            info: 元数据字典，可包含:
                - title: 标题
                - version: 版本
                - author: 作者
                - date: 日期
                - purpose: 目的
                - copyright: 版权
            on_version_conflict: 版本冲突处理策略
                - "ask": 返回冲突信息供用户确认
                - "use_first": 使用第一个文件的 IFC 版本
                - "error": 抛出错误
            validate: 是否进行 XSD 校验

        Returns:
            合并报告字典，包含:
            - output_file: 输出文件路径
            - total_specifications: 规范总数
            - source_files: 源文件列表
            - ifc_versions: IFC 版本信息
            - validation_passed: 校验是否通过
        """
        if not ids_files:
            raise IDSMergeError("No IDS files provided for merging")

        logger.info(f"Merging {len(ids_files)} IDS files...")

        # 1. 解析所有 IDS 文件
        parsed_files = []
        for file_path in ids_files:
            logger.info(f"Parsing: {file_path}")
            parsed = self._parse_ids_file(file_path)
            parsed_files.append(parsed)

        # 2. 提取元数据
        merged_info = self._extract_info(parsed_files, info)
        logger.info(f"Info: title='{merged_info.get('title', 'N/A')}'")

        # 3. 收集所有 specifications
        all_specifications = []
        for parsed in parsed_files:
            all_specifications.extend(parsed['specifications'])

        logger.info(f"Total specifications collected: {len(all_specifications)}")

        # 4. 检查 IFC 版本
        version_info = self._check_ifc_versions(all_specifications)
        logger.info(f"IFC versions: {version_info}")

        if not version_info['is_uniform'] and on_version_conflict == "error":
            raise IFCVersionConflictError(version_info['versions'])

        # 5. 构建合并后的 XML
        merged_xml = self._build_merged_xml(
            merged_info,
            all_specifications,
            version_info,
            on_version_conflict
        )

        # 6. XSD 校验
        validation_passed = True
        if validate:
            logger.info("Validating merged XML against XSD schema...")
            validation_passed = self._validate_xml(merged_xml)
            if validation_passed:
                logger.info("XSD validation passed!")
            else:
                logger.warning("XSD validation failed!")

        # 7. 保存文件
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Serialize to bytes first (for XML declaration), then decode
        xml_bytes = etree.tostring(
            merged_xml,
            encoding='utf-8',
            pretty_print=True,
            xml_declaration=True,
            standalone=True
        )

        with open(output_path, 'wb') as f:
            f.write(xml_bytes)

        logger.info(f"Merged IDS saved to: {output_path}")

        # 8. 生成报告
        report = {
            "output_file": str(output_path),
            "total_specifications": len(all_specifications),
            "source_files": [str(f) for f in ids_files],
            "ifc_versions": version_info,
            "info": merged_info,
            "validation_passed": validation_passed
        }

        return report

    def _parse_ids_file(self, file_path: str) -> Dict[str, Any]:
        """解析单个 IDS 文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = etree.parse(f)

        root = tree.getroot()

        # 提取 info
        info = {}
        info_elem = root.find('ids:info', NAMESPACES)
        if info_elem is not None:
            for child in info_elem:
                tag = etree.QName(child).localname
                info[tag] = child.text or ""

        # 提取 specifications
        specifications = []
        specs_elem = root.find('ids:specifications', NAMESPACES)
        if specs_elem is not None:
            for spec_elem in specs_elem:
                spec = {
                    'element': spec_elem,
                    'name': spec_elem.get('name', 'Unknown'),
                    'ifc_version': spec_elem.get('ifcVersion', 'Unknown')
                }
                specifications.append(spec)

        return {
            'file_path': file_path,
            'info': info,
            'specifications': specifications,
            'root': root
        }

    def _extract_info(
        self,
        parsed_files: List[Dict],
        override_info: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """提取并合并元数据"""
        # 默认使用第一个文件的 info
        merged_info = dict(parsed_files[0]['info'])

        # 如果用户提供了覆盖信息，使用用户的
        if override_info:
            merged_info.update(override_info)

        # 确保必要字段存在
        if 'title' not in merged_info:
            merged_info['title'] = 'Merged IDS Specification'
        if 'version' not in merged_info:
            merged_info['version'] = '1.0'
        if 'date' not in merged_info:
            merged_info['date'] = str(date.today())

        return merged_info

    def _check_ifc_versions(
        self,
        specifications: List[Dict]
    ) -> Dict[str, Any]:
        """检查所有规范的 IFC 版本"""
        version_map: Dict[str, List[str]] = {}

        for spec in specifications:
            version = spec['ifc_version']
            name = spec['name']

            if version not in version_map:
                version_map[version] = []
            version_map[version].append(name)

        is_uniform = len(version_map) == 1

        return {
            'is_uniform': is_uniform,
            'versions': version_map,
            'primary_version': list(version_map.keys())[0] if version_map else None
        }

    def _build_merged_xml(
        self,
        info: Dict[str, str],
        specifications: List[Dict],
        version_info: Dict,
        on_version_conflict: str
    ) -> etree._Element:
        """构建合并后的 XML 树"""
        # 创建根元素
        root = etree.Element(
            '{http://standards.buildingsmart.org/IDS}ids',
            nsmap=NSMAP
        )

        # 添加 xsi:schemaLocation 属性
        root.set(
            '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation',
            'http://standards.buildingsmart.org/IDS http://standards.buildingsmart.org/IDS/1.0/ids.xsd'
        )

        # 构建 info 元素
        info_elem = etree.SubElement(root, '{http://standards.buildingsmart.org/IDS}info')

        info_fields = ['title', 'version', 'author', 'date', 'purpose', 'copyright']
        for field in info_fields:
            if field in info and info[field]:
                field_elem = etree.SubElement(info_elem, f'{{http://standards.buildingsmart.org/IDS}}{field}')
                field_elem.text = info[field]

        # 构建 specifications 元素
        specs_elem = etree.SubElement(root, '{http://standards.buildingsmart.org/IDS}specifications')

        # 确定 IFC 版本
        primary_version = version_info['primary_version']

        for spec in specifications:
            spec_elem = spec['element']

            # 如果版本不统一，根据策略处理
            if not version_info['is_uniform']:
                if on_version_conflict == "use_first":
                    # 强制使用主版本
                    spec_elem.set('ifcVersion', primary_version)
                # "ask" 模式下保留原始版本

            # 深拷贝 specification 元素
            specs_elem.append(copy.deepcopy(spec_elem))

        return root

    def _validate_xml(self, root: etree._Element) -> bool:
        """验证 XML 是否符合 XSD Schema"""
        schema = self._load_schema()

        if not schema.validate(root):
            errors = list(schema.error_log)
            for error in errors:
                logger.error(f"XSD error at line {error.line}: {error.message}")
            return False

        return True

    def merge_from_directory(
        self,
        directory: str,
        output_path: str,
        pattern: str = "*.ids",
        **kwargs
    ) -> Dict[str, Any]:
        """
        合并目录下的所有 IDS 文件

        Args:
            directory: 目录路径
            output_path: 输出文件路径
            pattern: 文件匹配模式，默认 "*.ids"
            **kwargs: 传递给 merge() 的其他参数

        Returns:
            合并报告
        """
        dir_path = Path(directory)
        if not dir_path.is_dir():
            raise IDSMergeError(f"Directory not found: {directory}")

        ids_files = sorted(dir_path.glob(pattern))

        if not ids_files:
            raise IDSMergeError(f"No IDS files found in: {directory}")

        return self.merge([str(f) for f in ids_files], output_path, **kwargs)


# =============================================================================
# 便捷函数
# =============================================================================

def merge_ids_files(
    ids_files: List[str],
    output_path: str,
    **kwargs
) -> Dict[str, Any]:
    """
    合并多个 IDS 文件的便捷函数

    Args:
        ids_files: IDS 文件路径列表
        output_path: 输出文件路径
        **kwargs: 传递给 IDSMerger.merge() 的参数

    Returns:
        合并报告
    """
    merger = IDSMerger()
    return merger.merge(ids_files, output_path, **kwargs)


# =============================================================================
# CLI 入口
# =============================================================================

def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Merge multiple IDS XML files into one"
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="IDS files to merge"
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output file path"
    )
    parser.add_argument(
        "--title",
        help="Override title"
    )
    parser.add_argument(
        "--author",
        help="Override author"
    )
    parser.add_argument(
        "--version",
        help="Override version"
    )
    parser.add_argument(
        "--on-version-conflict",
        choices=["ask", "use_first", "error"],
        default="ask",
        help="How to handle IFC version conflicts"
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip XSD validation"
    )
    parser.add_argument(
        "--report",
        help="Path to save merge report (JSON)"
    )

    args = parser.parse_args()

    # 构建 info 覆盖
    info = {}
    if args.title:
        info['title'] = args.title
    if args.author:
        info['author'] = args.author
    if args.version:
        info['version'] = args.version

    # 执行合并
    merger = IDSMerger()
    report = merger.merge(
        args.files,
        args.output,
        info=info if info else None,
        on_version_conflict=args.on_version_conflict,
        validate=not args.no_validate
    )

    # 保存报告
    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info(f"Merge report saved to: {args.report}")

    # 打印摘要
    print("\n" + "=" * 60)
    print("IDS Merge Complete!")
    print("=" * 60)
    print(f"Output: {report['output_file']}")
    print(f"Total specifications: {report['total_specifications']}")
    print(f"IFC versions: {report['ifc_versions']['versions']}")
    print(f"Validation: {'PASSED' if report['validation_passed'] else 'FAILED'}")


if __name__ == "__main__":
    main()