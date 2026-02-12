"""
IFC数据模型定义

该模块定义了IFC实体、属性集和属性等数据模型，
用于向量数据库和规范化。
"""

from enum import Enum
from typing import Dict, List, Optional, Any


class IFCVersion(str, Enum):
    """支持的IFC版本"""

    IFC2X3 = "IFC2X3"
    IFC4 = "IFC4"
    IFC4X3 = "IFC4X3"


class IFCItemType(str, Enum):
    """IFC项目类型枚举"""
    ENTITY = "entity"
    PROPERTY_SET = "propertySet"
    PROPERTY = "property"
    ATTRIBUTE = "attribute"
    PART_OF = "partOf"
    CLASSIFICATION = "classification"
    MATERIAL = "material"


class IFCItem:
    """IFC项目（实体、属性集或属性）基类"""

    def __init__(
        self,
        name: str,
        definition: str,
        ifc_version: IFCVersion,
        item_type: IFCItemType = IFCItemType.ENTITY,
    ):
        self.name = name
        self.definition = definition
        self.ifc_version = ifc_version
        self.item_type = item_type

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "name": self.name,
            "definition": self.definition,
            "ifc_version": self.ifc_version,
            "item_type": self.item_type,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IFCItem":
        """从字典创建对象"""
        return cls(
            name=data["name"],
            definition=data["definition"],
            ifc_version=data["ifc_version"],
            item_type=data.get("item_type", IFCItemType.ENTITY),
        )

    def __str__(self) -> str:
        return f"{self.name} ({self.ifc_version}, {self.item_type}): {self.definition}"


class IFCEntity(IFCItem):
    """IFC实体类"""

    def __init__(
        self,
        name: str,
        definition: str,
        ifc_version: IFCVersion,
        predefined_types: Optional[List[str]] = None,
    ):
        super().__init__(name, definition, ifc_version, IFCItemType.ENTITY)
        self.predefined_types = predefined_types or []

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        data = super().to_dict()
        data["predefined_types"] = self.predefined_types
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IFCEntity":
        """从字典创建对象"""
        return cls(
            name=data["name"],
            definition=data["definition"],
            ifc_version=data["ifc_version"],
            predefined_types=data.get("predefined_types", []),
        )


class IFCPropertySet(IFCItem):
    """IFC属性集类"""

    def __init__(
        self,
        name: str,
        definition: str,
        ifc_version: IFCVersion,
        applicable_entities: Optional[List[str]] = None,
    ):
        super().__init__(name, definition, ifc_version, IFCItemType.PROPERTY_SET)
        self.applicable_entities = applicable_entities or []

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        data = super().to_dict()
        data["applicable_entities"] = self.applicable_entities
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IFCPropertySet":
        """从字典创建对象"""
        return cls(
            name=data["name"],
            definition=data["definition"],
            ifc_version=data["ifc_version"],
            applicable_entities=data.get("applicable_entities", []),
        )


class IFCProperty(IFCItem):
    """IFC属性类"""

    def __init__(
        self,
        name: str,
        definition: str,
        ifc_version: IFCVersion,
        property_set: Optional[str] = None,
        data_type: Optional[str] = None,
    ):
        super().__init__(name, definition, ifc_version, IFCItemType.PROPERTY)
        self.property_set = property_set
        self.data_type = data_type

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        data = super().to_dict()
        data["property_set"] = self.property_set
        data["data_type"] = self.data_type
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IFCProperty":
        """从字典创建对象"""
        return cls(
            name=data["name"],
            definition=data["definition"],
            ifc_version=data["ifc_version"],
            property_set=data.get("property_set"),
            data_type=data.get("data_type"),
        )


class IFCAttribute(IFCItem):
    """IFC属性类"""

    def __init__(
        self,
        name: str,
        definition: str,
        ifc_version: IFCVersion,
        entity: Optional[str] = None,
        data_type: Optional[str] = None,
    ):
        super().__init__(name, definition, ifc_version, IFCItemType.ATTRIBUTE)
        self.entity = entity
        self.data_type = data_type

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        data = super().to_dict()
        data["entity"] = self.entity
        data["data_type"] = self.data_type
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IFCAttribute":
        """从字典创建对象"""
        return cls(
            name=data["name"],
            definition=data["definition"],
            ifc_version=data["ifc_version"],
            entity=data.get("entity"),
            data_type=data.get("data_type"),
        )


class IFCPartOf(IFCItem):
    """IFC部分关系类，表示实体与实体之间的组成关系"""

    def __init__(
        self,
        name: str,
        definition: str,
        ifc_version: IFCVersion,
        parent_entity: Optional[str] = None,
        child_entity: Optional[str] = None,
        relationship_type: Optional[str] = None,
    ):
        super().__init__(name, definition, ifc_version, IFCItemType.PART_OF)
        self.parent_entity = parent_entity
        self.child_entity = child_entity
        self.relationship_type = relationship_type

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        data = super().to_dict()
        data["parent_entity"] = self.parent_entity
        data["child_entity"] = self.child_entity
        data["relationship_type"] = self.relationship_type
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IFCPartOf":
        """从字典创建对象"""
        return cls(
            name=data["name"],
            definition=data["definition"],
            ifc_version=data["ifc_version"],
            parent_entity=data.get("parent_entity"),
            child_entity=data.get("child_entity"),
            relationship_type=data.get("relationship_type"),
        )


class IFCClassification(IFCItem):
    """IFC分类类，表示实体的分类信息"""

    def __init__(
        self,
        name: str,
        definition: str,
        ifc_version: IFCVersion,
        classification_system: Optional[str] = None,
        classification_code: Optional[str] = None,
        applicable_entities: Optional[List[str]] = None,
    ):
        super().__init__(name, definition, ifc_version, IFCItemType.CLASSIFICATION)
        self.classification_system = classification_system
        self.classification_code = classification_code
        self.applicable_entities = applicable_entities or []

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        data = super().to_dict()
        data["classification_system"] = self.classification_system
        data["classification_code"] = self.classification_code
        data["applicable_entities"] = self.applicable_entities
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IFCClassification":
        """从字典创建对象"""
        return cls(
            name=data["name"],
            definition=data["definition"],
            ifc_version=data["ifc_version"],
            classification_system=data.get("classification_system"),
            classification_code=data.get("classification_code"),
            applicable_entities=data.get("applicable_entities", []),
        )


class IFCMaterial(IFCItem):
    """IFC材料类，表示实体的材料信息"""

    def __init__(
        self,
        name: str,
        definition: str,
        ifc_version: IFCVersion,
        category: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
        applicable_entities: Optional[List[str]] = None,
    ):
        super().__init__(name, definition, ifc_version, IFCItemType.MATERIAL)
        self.category = category
        self.properties = properties or {}
        self.applicable_entities = applicable_entities or []

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        data = super().to_dict()
        data["category"] = self.category
        data["properties"] = self.properties
        data["applicable_entities"] = self.applicable_entities
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IFCMaterial":
        """从字典创建对象"""
        return cls(
            name=data["name"],
            definition=data["definition"],
            ifc_version=data["ifc_version"],
            category=data.get("category"),
            properties=data.get("properties", {}),
            applicable_entities=data.get("applicable_entities", []),
        )
