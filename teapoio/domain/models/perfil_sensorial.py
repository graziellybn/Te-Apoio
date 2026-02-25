from dataclasses import dataclass


@dataclass
class PerfilSensorial:
    tatil_sensibilidades: str = ""
    tatil_preferencias: str = ""
    auditivo_sensibilidades: str = ""
    auditivo_preferencias: str = ""
    visual_sensibilidades: str = ""
    visual_preferencias: str = ""

    def to_dict(self) -> dict:
        return {
            "tatil_sensibilidades": self.tatil_sensibilidades,
            "tatil_preferencias": self.tatil_preferencias,
            "auditivo_sensibilidades": self.auditivo_sensibilidades,
            "auditivo_preferencias": self.auditivo_preferencias,
            "visual_sensibilidades": self.visual_sensibilidades,
            "visual_preferencias": self.visual_preferencias,
        }

    @staticmethod
    def from_dict(data: dict) -> "PerfilSensorial":
        return PerfilSensorial(
            tatil_sensibilidades=data.get("tatil_sensibilidades", ""),
            tatil_preferencias=data.get("tatil_preferencias", ""),
            auditivo_sensibilidades=data.get("auditivo_sensibilidades", ""),
            auditivo_preferencias=data.get("auditivo_preferencias", ""),
            visual_sensibilidades=data.get("visual_sensibilidades", ""),
            visual_preferencias=data.get("visual_preferencias", ""),
        )
