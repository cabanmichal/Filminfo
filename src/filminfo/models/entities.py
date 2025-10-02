from dataclasses import asdict, dataclass, field
from enum import Enum
from math import isclose
from typing import Any, Protocol, TypeVar


T = TypeVar("T")

COUNTRIES = [
    ("Afghanistan", "AF", "AFG"),
    ("Albania", "AL", "ALB"),
    ("Algeria", "DZ", "DZA"),
    ("American Samoa", "AS", "ASM"),
    ("Andorra", "AD", "AND"),
    ("Angola", "AO", "AGO"),
    ("Anguilla", "AI", "AIA"),
    ("Antarctica", "AQ", "ATA"),
    ("Antigua and Barbuda", "AG", "ATG"),
    ("Argentina", "AR", "ARG"),
    ("Armenia", "AM", "ARM"),
    ("Aruba", "AW", "ABW"),
    ("Australia", "AU", "AUS"),
    ("Austria", "AT", "AUT"),
    ("Azerbaijan", "AZ", "AZE"),
    ("Åland Islands", "AX", "ALA"),
    ("Bahamas", "BS", "BHS"),
    ("Bahrain", "BH", "BHR"),
    ("Bangladesh", "BD", "BGD"),
    ("Barbados", "BB", "BRB"),
    ("Belarus", "BY", "BLR"),
    ("Belgium", "BE", "BEL"),
    ("Belize", "BZ", "BLZ"),
    ("Benin", "BJ", "BEN"),
    ("Bermuda", "BM", "BMU"),
    ("Bhutan", "BT", "BTN"),
    ("Bolivia (Plurinational State of)", "BO", "BOL"),
    ("Bonaire, Sint Eustatius and Saba", "BQ", "BES"),
    ("Bosnia and Herzegovina", "BA", "BIH"),
    ("Botswana", "BW", "BWA"),
    ("Bouvet Island", "BV", "BVT"),
    ("Brazil", "BR", "BRA"),
    ("British Indian Ocean Territory", "IO", "IOT"),
    ("Brunei Darussalam", "BN", "BRN"),
    ("Bulgaria", "BG", "BGR"),
    ("Burkina Faso", "BF", "BFA"),
    ("Burundi", "BI", "BDI"),
    ("Cabo Verde", "CV", "CPV"),
    ("Cambodia", "KH", "KHM"),
    ("Cameroon", "CM", "CMR"),
    ("Canada", "CA", "CAN"),
    ("Cayman Islands", "KY", "CYM"),
    ("Central African Republic", "CF", "CAF"),
    ("Chad", "TD", "TCD"),
    ("Chile", "CL", "CHL"),
    ("China", "CN", "CHN"),
    ("Christmas Island", "CX", "CXR"),
    ("Cocos (Keeling) Islands", "CC", "CCK"),
    ("Colombia", "CO", "COL"),
    ("Comoros", "KM", "COM"),
    ("Congo", "CG", "COG"),
    ("Congo, Democratic Republic of the", "CD", "COD"),
    ("Cook Islands", "CK", "COK"),
    ("Costa Rica", "CR", "CRI"),
    ("Croatia", "HR", "HRV"),
    ("Cuba", "CU", "CUB"),
    ("Curaçao", "CW", "CUW"),
    ("Cyprus", "CY", "CYP"),
    ("Czech Republic", "CZ", "CZE"),
    ("Côte d'Ivoire", "CI", "CIV"),
    ("Denmark", "DK", "DNK"),
    ("Djibouti", "DJ", "DJI"),
    ("Dominica", "DM", "DMA"),
    ("Dominican Republic", "DO", "DOM"),
    ("Ecuador", "EC", "ECU"),
    ("Egypt", "EG", "EGY"),
    ("El Salvador", "SV", "SLV"),
    ("Equatorial Guinea", "GQ", "GNQ"),
    ("Eritrea", "ER", "ERI"),
    ("Estonia", "EE", "EST"),
    ("Eswatini", "SZ", "SWZ"),
    ("Ethiopia", "ET", "ETH"),
    ("Falkland Islands (Malvinas)", "FK", "FLK"),
    ("Faroe Islands", "FO", "FRO"),
    ("Fiji", "FJ", "FJI"),
    ("Finland", "FI", "FIN"),
    ("France", "FR", "FRA"),
    ("French Guiana", "GF", "GUF"),
    ("French Polynesia", "PF", "PYF"),
    ("French Southern Territories", "TF", "ATF"),
    ("Gabon", "GA", "GAB"),
    ("Gambia", "GM", "GMB"),
    ("Georgia", "GE", "GEO"),
    ("Germany", "DE", "DEU"),
    ("Ghana", "GH", "GHA"),
    ("Gibraltar", "GI", "GIB"),
    ("Greece", "GR", "GRC"),
    ("Greenland", "GL", "GRL"),
    ("Grenada", "GD", "GRD"),
    ("Guadeloupe", "GP", "GLP"),
    ("Guam", "GU", "GUM"),
    ("Guatemala", "GT", "GTM"),
    ("Guernsey", "GG", "GGY"),
    ("Guinea", "GN", "GIN"),
    ("Guinea-Bissau", "GW", "GNB"),
    ("Guyana", "GY", "GUY"),
    ("Haiti", "HT", "HTI"),
    ("Heard Island and McDonald Islands", "HM", "HMD"),
    ("Holy See (Vatican City State)", "VA", "VAT"),
    ("Honduras", "HN", "HND"),
    ("Hong Kong", "HK", "HKG"),
    ("Hungary", "HU", "HUN"),
    ("Iceland", "IS", "ISL"),
    ("India", "IN", "IND"),
    ("Indonesia", "ID", "IDN"),
    ("Iran (Islamic Republic of)", "IR", "IRN"),
    ("Iraq", "IQ", "IRQ"),
    ("Ireland", "IE", "IRL"),
    ("Isle of Man", "IM", "IMN"),
    ("Israel", "IL", "ISR"),
    ("Italy", "IT", "ITA"),
    ("Jamaica", "JM", "JAM"),
    ("Japan", "JP", "JPN"),
    ("Jersey", "JE", "JEY"),
    ("Jordan", "JO", "JOR"),
    ("Kazakhstan", "KZ", "KAZ"),
    ("Kenya", "KE", "KEN"),
    ("Kiribati", "KI", "KIR"),
    ("Korea, Democratic People's Republic of", "KP", "PRK"),
    ("Korea (Republic of)", "KR", "KOR"),
    ("Kuwait", "KW", "KWT"),
    ("Kyrgyzstan", "KG", "KGZ"),
    ("Lao People’s Democratic Republic", "LA", "LAO"),
    ("Latvia", "LV", "LVA"),
    ("Lebanon", "LB", "LBN"),
    ("Lesotho", "LS", "LSO"),
    ("Liberia", "LR", "LBR"),
    ("Libya", "LY", "LBY"),
    ("Liechtenstein", "LI", "LIE"),
    ("Lithuania", "LT", "LTU"),
    ("Luxembourg", "LU", "LUX"),
    ("Macao", "MO", "MAC"),
    ("Madagascar", "MG", "MDG"),
    ("Malawi", "MW", "MWI"),
    ("Malaysia", "MY", "MYS"),
    ("Maldives", "MV", "MDV"),
    ("Mali", "ML", "MLI"),
    ("Malta", "MT", "MLT"),
    ("Marshall Islands", "MH", "MHL"),
    ("Martinique", "MQ", "MTQ"),
    ("Mauritania", "MR", "MRT"),
    ("Mauritius", "MU", "MUS"),
    ("Mayotte", "YT", "MYT"),
    ("Mexico", "MX", "MEX"),
    ("Micronesia (Federated States of)", "FM", "FSM"),
    ("Moldova (Republic of)", "MD", "MDA"),
    ("Monaco", "MC", "MCO"),
    ("Mongolia", "MN", "MNG"),
    ("Montenegro", "ME", "MNE"),
    ("Montserrat", "MS", "MSR"),
    ("Morocco", "MA", "MAR"),
    ("Mozambique", "MZ", "MOZ"),
    ("Myanmar", "MM", "MMR"),
    ("Namibia", "NA", "NAM"),
    ("Nauru", "NR", "NRU"),
    ("Nepal", "NP", "NPL"),
    ("Netherlands (Kingdom of the)", "NL", "NLD"),
    ("New Caledonia", "NC", "NCL"),
    ("New Zealand", "NZ", "NZL"),
    ("Nicaragua", "NI", "NIC"),
    ("Niger", "NE", "NER"),
    ("Nigeria", "NG", "NGA"),
    ("Niue", "NU", "NIU"),
    ("Norfolk Island", "NF", "NFK"),
    ("North Macedonia", "MK", "MKD"),
    ("Northern Mariana Islands", "MP", "MNP"),
    ("Norway", "NO", "NOR"),
    ("Oman", "OM", "OMN"),
    ("Pakistan", "PK", "PAK"),
    ("Palau", "PW", "PLW"),
    ("Palestine, State of", "PS", "PSE"),
    ("Panama", "PA", "PAN"),
    ("Papua New Guinea", "PG", "PNG"),
    ("Paraguay", "PY", "PRY"),
    ("Peru", "PE", "PER"),
    ("Philippines", "PH", "PHL"),
    ("Pitcairn", "PN", "PCN"),
    ("Poland", "PL", "POL"),
    ("Portugal", "PT", "PRT"),
    ("Puerto Rico", "PR", "PRI"),
    ("Qatar", "QA", "QAT"),
    ("Romania", "RO", "ROU"),
    ("Russian Federation", "RU", "RUS"),
    ("Rwanda", "RW", "RWA"),
    ("Réunion", "RE", "REU"),
    ("Saint Barthélemy", "BL", "BLM"),
    ("Saint Helena, Ascension and Tristan da Cunha", "SH", "SHN"),
    ("Saint Kitts and Nevis", "KN", "KNA"),
    ("Saint Lucia", "LC", "LCA"),
    ("Saint Martin (French part)", "MF", "MAF"),
    ("Saint Pierre and Miquelon", "PM", "SPM"),
    ("Saint Vincent and the Grenadines", "VC", "VCT"),
    ("Samoa", "WS", "WSM"),
    ("San Marino", "SM", "SMR"),
    ("Sao Tome and Principe", "ST", "STP"),
    ("Saudi Arabia", "SA", "SAU"),
    ("Senegal", "SN", "SEN"),
    ("Serbia", "RS", "SRB"),
    ("Seychelles", "SC", "SYC"),
    ("Sierra Leone", "SL", "SLE"),
    ("Singapore", "SG", "SGP"),
    ("Sint Maarten (Dutch part)", "SX", "SXM"),
    ("Slovakia", "SK", "SVK"),
    ("Slovenia", "SI", "SVN"),
    ("Solomon Islands", "SB", "SLB"),
    ("Somalia", "SO", "SOM"),
    ("South Africa", "ZA", "ZAF"),
    ("South Georgia and the South Sandwich Islands", "GS", "SGS"),
    ("South Sudan", "SS", "SSD"),
    ("Spain", "ES", "ESP"),
    ("Sri Lanka", "LK", "LKA"),
    ("Sudan", "SD", "SDN"),
    ("Suriname", "SR", "SUR"),
    ("Svalbard and Jan Mayen", "SJ", "SJM"),
    ("Sweden", "SE", "SWE"),
    ("Switzerland", "CH", "CHE"),
    ("Syrian Arab Republic", "SY", "SYR"),
    ("Taiwan, Province of China", "TW", "TWN"),
    ("Tajikistan", "TJ", "TJK"),
    ("Tanzania, United Republic of", "TZ", "TZA"),
    ("Thailand", "TH", "THA"),
    ("Timor-Leste", "TL", "TLS"),
    ("Togo", "TG", "TGO"),
    ("Tokelau", "TK", "TKL"),
    ("Tonga", "TO", "TON"),
    ("Trinidad and Tobago", "TT", "TTO"),
    ("Tunisia", "TN", "TUN"),
    ("Turkmenistan", "TM", "TKM"),
    ("Turks and Caicos Islands", "TC", "TCA"),
    ("Tuvalu", "TV", "TUV"),
    ("Türkiye", "TR", "TUR"),
    ("Uganda", "UG", "UGA"),
    ("Ukraine", "UA", "UKR"),
    ("United Arab Emirates", "AE", "ARE"),
    ("United Kingdom of Great Britain and Northern Ireland", "GB", "GBR"),
    ("United States Minor Outlying Islands", "UM", "UMI"),
    ("United States of America", "US", "USA"),
    ("Uruguay", "UY", "URY"),
    ("Uzbekistan", "UZ", "UZB"),
    ("Vanuatu", "VU", "VUT"),
    ("Venezuela (Bolivarian Republic of)", "VE", "VEN"),
    ("Viet Nam", "VN", "VNM"),
    ("Virgin Islands (British)", "VG", "VGB"),
    ("Virgin Islands (U.S.)", "VI", "VIR"),
    ("Wallis and Futuna", "WF", "WLF"),
    ("Western Sahara", "EH", "ESH"),
    ("Yemen", "YE", "YEM"),
    ("Zambia", "ZM", "ZMB"),
    ("Zimbabwe", "ZW", "ZWE"),
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
