from dataclasses import asdict, dataclass, field
from enum import Enum
from math import isclose
from typing import Any, Protocol, TypeVar


T = TypeVar("T")

COUNTRIES = [
    ("Afghanistan", "AF"),
    ("Albania", "AL"),
    ("Algeria", "DZ"),
    ("American Samoa", "AS"),
    ("Andorra", "AD"),
    ("Angola", "AO"),
    ("Anguilla", "AI"),
    ("Antarctica", "AQ"),
    ("Antigua and Barbuda", "AG"),
    ("Argentina", "AR"),
    ("Armenia", "AM"),
    ("Aruba", "AW"),
    ("Australia", "AU"),
    ("Austria", "AT"),
    ("Azerbaijan", "AZ"),
    ("Åland Islands", "AX"),
    ("Bahamas", "BS"),
    ("Bahrain", "BH"),
    ("Bangladesh", "BD"),
    ("Barbados", "BB"),
    ("Belarus", "BY"),
    ("Belgium", "BE"),
    ("Belize", "BZ"),
    ("Benin", "BJ"),
    ("Bermuda", "BM"),
    ("Bhutan", "BT"),
    ("Bolivia, Plurinational State of", "BO"),
    ("Bonaire, Sint Eustatius and Saba", "BQ"),
    ("Bosnia and Herzegovina", "BA"),
    ("Botswana", "BW"),
    ("Bouvet Island", "BV"),
    ("Brazil", "BR"),
    ("British Indian Ocean Territory", "IO"),
    ("Brunei Darussalam", "BN"),
    ("Bulgaria", "BG"),
    ("Burkina Faso", "BF"),
    ("Burundi", "BI"),
    ("Cabo Verde", "CV"),
    ("Cambodia", "KH"),
    ("Cameroon", "CM"),
    ("Canada", "CA"),
    ("Cayman Islands", "KY"),
    ("Central African Republic", "CF"),
    ("Chad", "TD"),
    ("Chile", "CL"),
    ("China", "CN"),
    ("Christmas Island", "CX"),
    ("Cocos (Keeling) Islands", "CC"),
    ("Colombia", "CO"),
    ("Comoros", "KM"),
    ("Congo", "CG"),
    ("Congo, Democratic Republic of the", "CD"),
    ("Cook Islands", "CK"),
    ("Costa Rica", "CR"),
    ("Croatia", "HR"),
    ("Cuba", "CU"),
    ("Curaçao", "CW"),
    ("Cyprus", "CY"),
    ("Czechia", "CZ"),
    ("Côte d'Ivoire", "CI"),
    ("Denmark", "DK"),
    ("Djibouti", "DJ"),
    ("Dominica", "DM"),
    ("Dominican Republic", "DO"),
    ("Ecuador", "EC"),
    ("Egypt", "EG"),
    ("El Salvador", "SV"),
    ("Equatorial Guinea", "GQ"),
    ("Eritrea", "ER"),
    ("Estonia", "EE"),
    ("Eswatini", "SZ"),
    ("Ethiopia", "ET"),
    ("Falkland Islands (Malvinas)", "FK"),
    ("Faroe Islands", "FO"),
    ("Fiji", "FJ"),
    ("Finland", "FI"),
    ("France", "FR"),
    ("French Guiana", "GF"),
    ("French Polynesia", "PF"),
    ("French Southern Territories", "TF"),
    ("Gabon", "GA"),
    ("Gambia", "GM"),
    ("Georgia", "GE"),
    ("Germany", "DE"),
    ("Ghana", "GH"),
    ("Gibraltar", "GI"),
    ("Greece", "GR"),
    ("Greenland", "GL"),
    ("Grenada", "GD"),
    ("Guadeloupe", "GP"),
    ("Guam", "GU"),
    ("Guatemala", "GT"),
    ("Guernsey", "GG"),
    ("Guinea", "GN"),
    ("Guinea-Bissau", "GW"),
    ("Guyana", "GY"),
    ("Haiti", "HT"),
    ("Heard Island and McDonald Islands", "HM"),
    ("Holy See", "VA"),
    ("Honduras", "HN"),
    ("Hong Kong", "HK"),
    ("Hungary", "HU"),
    ("Iceland", "IS"),
    ("India", "IN"),
    ("Indonesia", "ID"),
    ("Iran, Islamic Republic of", "IR"),
    ("Iraq", "IQ"),
    ("Ireland", "IE"),
    ("Isle of Man", "IM"),
    ("Israel", "IL"),
    ("Italy", "IT"),
    ("Jamaica", "JM"),
    ("Japan", "JP"),
    ("Jersey", "JE"),
    ("Jordan", "JO"),
    ("Kazakhstan", "KZ"),
    ("Kenya", "KE"),
    ("Kiribati", "KI"),
    ("Korea, Democratic People's Republic of", "KP"),
    ("Korea, Republic of", "KR"),
    ("Kuwait", "KW"),
    ("Kyrgyzstan", "KG"),
    ("Lao People's Democratic Republic", "LA"),
    ("Latvia", "LV"),
    ("Lebanon", "LB"),
    ("Lesotho", "LS"),
    ("Liberia", "LR"),
    ("Libya", "LY"),
    ("Liechtenstein", "LI"),
    ("Lithuania", "LT"),
    ("Luxembourg", "LU"),
    ("Macao", "MO"),
    ("Madagascar", "MG"),
    ("Malawi", "MW"),
    ("Malaysia", "MY"),
    ("Maldives", "MV"),
    ("Mali", "ML"),
    ("Malta", "MT"),
    ("Marshall Islands", "MH"),
    ("Martinique", "MQ"),
    ("Mauritania", "MR"),
    ("Mauritius", "MU"),
    ("Mayotte", "YT"),
    ("Mexico", "MX"),
    ("Micronesia, Federated States of", "FM"),
    ("Moldova, Republic of", "MD"),
    ("Monaco", "MC"),
    ("Mongolia", "MN"),
    ("Montenegro", "ME"),
    ("Montserrat", "MS"),
    ("Morocco", "MA"),
    ("Mozambique", "MZ"),
    ("Myanmar", "MM"),
    ("Namibia", "NA"),
    ("Nauru", "NR"),
    ("Nepal", "NP"),
    ("Netherlands, Kingdom of the", "NL"),
    ("New Caledonia", "NC"),
    ("New Zealand", "NZ"),
    ("Nicaragua", "NI"),
    ("Niger", "NE"),
    ("Nigeria", "NG"),
    ("Niue", "NU"),
    ("Norfolk Island", "NF"),
    ("North Macedonia", "MK"),
    ("Northern Mariana Islands", "MP"),
    ("Norway", "NO"),
    ("Oman", "OM"),
    ("Pakistan", "PK"),
    ("Palau", "PW"),
    ("Palestine, State of", "PS"),
    ("Panama", "PA"),
    ("Papua New Guinea", "PG"),
    ("Paraguay", "PY"),
    ("Peru", "PE"),
    ("Philippines", "PH"),
    ("Pitcairn", "PN"),
    ("Poland", "PL"),
    ("Portugal", "PT"),
    ("Puerto Rico", "PR"),
    ("Qatar", "QA"),
    ("Romania", "RO"),
    ("Russian Federation", "RU"),
    ("Rwanda", "RW"),
    ("Réunion", "RE"),
    ("Saint Barthélemy", "BL"),
    ("Saint Helena, Ascension and Tristan da Cunha", "SH"),
    ("Saint Kitts and Nevis", "KN"),
    ("Saint Lucia", "LC"),
    ("Saint Martin (French part)", "MF"),
    ("Saint Pierre and Miquelon", "PM"),
    ("Saint Vincent and the Grenadines", "VC"),
    ("Samoa", "WS"),
    ("San Marino", "SM"),
    ("Sao Tome and Principe", "ST"),
    ("Saudi Arabia", "SA"),
    ("Senegal", "SN"),
    ("Serbia", "RS"),
    ("Seychelles", "SC"),
    ("Sierra Leone", "SL"),
    ("Singapore", "SG"),
    ("Sint Maarten (Dutch part)", "SX"),
    ("Slovakia", "SK"),
    ("Slovenia", "SI"),
    ("Solomon Islands", "SB"),
    ("Somalia", "SO"),
    ("South Africa", "ZA"),
    ("South Georgia and the South Sandwich Islands", "GS"),
    ("South Sudan", "SS"),
    ("Spain", "ES"),
    ("Sri Lanka", "LK"),
    ("Sudan", "SD"),
    ("Suriname", "SR"),
    ("Svalbard and Jan Mayen", "SJ"),
    ("Sweden", "SE"),
    ("Switzerland", "CH"),
    ("Syrian Arab Republic", "SY"),
    ("Taiwan, Province of China[note 1]", "TW"),
    ("Tajikistan", "TJ"),
    ("Tanzania, United Republic of", "TZ"),
    ("Thailand", "TH"),
    ("Timor-Leste", "TL"),
    ("Togo", "TG"),
    ("Tokelau", "TK"),
    ("Tonga", "TO"),
    ("Trinidad and Tobago", "TT"),
    ("Tunisia", "TN"),
    ("Turkmenistan", "TM"),
    ("Turks and Caicos Islands", "TC"),
    ("Tuvalu", "TV"),
    ("Türkiye", "TR"),
    ("Uganda", "UG"),
    ("Ukraine", "UA"),
    ("United Arab Emirates", "AE"),
    ("United Kingdom of Great Britain and Northern Ireland", "GB"),
    ("United States Minor Outlying Islands", "UM"),
    ("United States of America", "US"),
    ("Uruguay", "UY"),
    ("Uzbekistan", "UZ"),
    ("Vanuatu", "VU"),
    ("Venezuela, Bolivarian Republic of", "VE"),
    ("Viet Nam", "VN"),
    ("Virgin Islands (British)", "VG"),
    ("Virgin Islands (U.S.)", "VI"),
    ("Wallis and Futuna", "WF"),
    ("Western Sahara", "EH"),
    ("Yemen", "YE"),
    ("Zambia", "ZM"),
    ("Zimbabwe", "ZW"),
]


class Serializable(Protocol):
    def to_dict(self) -> dict[str, Any]: ...

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T: ...


class CropFactor(Enum):
    FULL_FRAME = (1.0, "35mm")
    HALF_FRAME = (1.44, "Half frame")
    MEDIUM_645 = (0.62, "Medium format 6 x 4.5")
    MEDIUM_66 = (0.55, "Medium format 6 x 6")
    MEDIUM_67 = (0.48, "Medium format 6 x 7")
    MEDIUM_69 = (0.43, "Medium format 6 x 9")

    def __str__(self) -> str:
        return f"{self.value[0]:.2f} ({self.value[1]})"

    def as_float(self) -> float:
        return self.value[0]

    @classmethod
    def from_float(cls, value: float) -> "CropFactor| None":
        value, rest = divmod(value * 1000, 10)
        if rest > 4:
            value += 1

        value /= 100
        for member in cls:
            if isclose(member.value[0], value):
                return member
        return None


class FilmFormat(Enum):
    FILM_135 = "135"
    FILM_120 = "120"
    FILM_220 = "220"
    FILM_APS = "APS"
    FILM_116 = "116"
    FILM_616 = "616"
    FILM_127 = "127"
    FILM_828 = "828"
    FILM_620 = "620"
    FILM_126 = "126"
    FILM_110 = "110"
    FILM_16MM = "16mm"
    FILM_8MM = "8mm"


@dataclass(frozen=True, order=True)
class Film:
    make: str
    name: str
    iso: int
    format: str | None = field(default=None, compare=False, hash=False)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        del data["format"]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Film":
        make = data["make"]
        name = data["name"]
        iso = data["iso"]
        format = data.get("format")
        return Film(make, name, iso, format)


@dataclass(frozen=True, order=True)
class Camera:
    make: str
    model: str
    crop: float = CropFactor.FULL_FRAME.as_float()
    serial: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Camera":
        make = data["make"]
        model = data["model"]
        crop = data["crop"]
        serial = data["serial"]
        return Camera(make, model, crop, serial)


@dataclass(frozen=True, order=True)
class Lens:
    make: str
    model: str
    focal_length: list[float] = field(default_factory=list, compare=False, hash=False)
    serial: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Lens":
        make = data["make"]
        model = data["model"]
        focal_length = data["focal_length"]
        serial = data["serial"]
        return Lens(make, model, focal_length, serial)
