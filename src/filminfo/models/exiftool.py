import subprocess
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from filminfo.models.convertes import (
    exif_date_time_to_iptc,
    parse_focal_length,
    parse_shutter_speed,
    to_ascii,
)
from filminfo.models.entities import COUNTRIES, FLASH_VALUES
from filminfo.models.validators import (
    aperture_valid,
    date_taken_valid,
    focal_length_valid,
    iso_valid,
    latitude_valid,
    longitude_valid,
    resolution_valid,
    shutter_speed_valid,
)


ExifToolReply = tuple[Exception | None, str]


@dataclass
class RunResult:
    returncode: int
    stdout: str
    stderr: str
    info: str


class ExifTool:
    def __init__(self, exiftool_binary: Path):
        self._binary = str(exiftool_binary)

    def add_metadata(
        self, images: Sequence[str], metadata: dict[str, str]
    ) -> ExifToolReply:
        try:
            result = self._add_metadata(images, metadata)
            return None, result
        except Exception as err:
            return err, "Metadata writing not successful"

    def remove_metadata(
        self, images: Sequence[str], tags: Sequence[str]
    ) -> ExifToolReply:
        try:
            result = self._remove_metadata(images, tags)
            return None, result
        except Exception as err:
            return err, "Metadata removal not successful"

    def get_metadata(self, images: Sequence[str]) -> ExifToolReply:
        try:
            result = self._get_metadata(images)
            return None, result
        except Exception as err:
            return err, "Metadata retrieval not successful"

    def export_metadata(
        self, images: Sequence[str], output_file: Path
    ) -> ExifToolReply:
        try:
            result = self._export_metadata(images)
            with open(output_file, "w", encoding="utf-8") as ofh:
                ofh.write(result.stdout)
            return None, result.info
        except Exception as err:
            return err, "Metadata export not successful"

    def import_metadata(self, images: Sequence[str], input_file: Path) -> ExifToolReply:
        try:
            result = self._import_metadata(images, input_file)
            return None, result
        except Exception as err:
            return err, "Metadata import not successful"

    def _add_metadata(self, images: Sequence[str], medatada: dict[str, str]) -> str:
        if not images:
            raise ValueError("No files provided for metadata writing.")

        film_make = medatada.get("film_make")
        film_name = medatada.get("film_name")
        film_iso = medatada.get("film_iso")
        film_format = medatada.get("film_format")
        camera_make = medatada.get("camera_make")
        camera_model = medatada.get("camera_model")
        camera_crop = medatada.get("camera_crop")
        camera_serial = medatada.get("camera_serial")
        lens_make = medatada.get("lens_make")
        lens_model = medatada.get("lens_model")
        lens_focal_length = medatada.get("lens_focal_length")
        lens_serial = medatada.get("lens_serial")
        origin_author = medatada.get("origin_author")
        origin_copyright = medatada.get("origin_copyright")
        origin_city = medatada.get("origin_city")
        origin_sublocation = medatada.get("origin_sublocation")
        origin_country = medatada.get("origin_country")
        origin_gps_latitude = medatada.get("origin_gps_latitude")
        origin_gps_longitude = medatada.get("origin_gps_longitude")
        origin_date_taken = medatada.get("origin_date_taken")
        exposure_aperture = medatada.get("exposure_aperture")
        exposure_shutter_speed = medatada.get("exposure_shutter_speed")
        exposure_iso = medatada.get("exposure_iso")
        exposure_flash = medatada.get("exposure_flash")
        comments_description = medatada.get("comments_description")
        comments_user_comment = medatada.get("comments_user_comment")
        comments_auto_comment = medatada.get("comments_auto_comment")
        other_resolution = medatada.get("other_resolution")
        other_tags = medatada.get("other_tags")

        if not any(
            [
                film_make,
                film_name,
                film_iso,
                film_format,
                camera_make,
                camera_model,
                camera_crop,
                camera_serial,
                lens_make,
                lens_model,
                lens_focal_length,
                lens_serial,
                origin_author,
                origin_copyright,
                origin_city,
                origin_sublocation,
                origin_country,
                origin_gps_latitude,
                origin_gps_longitude,
                origin_date_taken,
                exposure_aperture,
                exposure_shutter_speed,
                exposure_iso,
                exposure_flash,
                comments_user_comment,
                comments_auto_comment,
                other_resolution,
                other_tags,
            ]
        ):
            raise ValueError("No metadata to write.")

        args = [
            self._binary,
            "-iptc:CodedCharacterSet=UTF8",
        ]

        # https://exiftool.org/TagNames/MWG.html
        if origin_author:
            args.append(f"-EXIF:Artist={origin_author}")
            args.append(f"-IPTC:By-line={to_ascii(origin_author)}")
            args.append(f"-XMP-dc:Creator={origin_author}")

        if origin_copyright:
            args.append(f"-EXIF:Copyright={origin_copyright}")
            args.append(f"-IPTC:CopyrightNotice={origin_copyright}")
            args.append(f"-XMP-dc:Rights={origin_copyright}")
            args.append("-XMP-xmpRights:Marked=True")

        if origin_date_taken:
            if not date_taken_valid(origin_date_taken):
                raise ValueError("Invalid date time format")
            args.append(f"-EXIF:DateTimeOriginal={origin_date_taken}")
            args.append(f"-XMP-photoshop:DateCreated={origin_date_taken}")
            iptc_date, iptc_time = exif_date_time_to_iptc(origin_date_taken)
            args.append(f"-IPTC:DateCreated={iptc_date}")
            args.append(f"-IPTC:TimeCreated={iptc_time}")

        if origin_country:
            country, code2, code3 = self._get_country_code(origin_country)
            args.append(f"-IPTC:Country-PrimaryLocationName={country}")
            args.append(f"-XMP-photoshop:Country={country}")
            args.append(f"-XMP-iptcExt:LocationShownCountryName={country}")

            if code3:
                args.append(f"-IPTC:Country-PrimaryLocationCode={code3}")
            if code2:
                args.append(f"-XMP-iptcCore:CountryCode={code2}")
                args.append(f"-XMP-iptcExt:LocationCreatedCountryCode={code2}")

        if origin_gps_latitude:
            if not latitude_valid(origin_gps_latitude):
                raise ValueError("Invalid latitude")
            value = float(origin_gps_latitude)
            ref = "S" if value < 0 else "N"
            args.append(f"-EXIF:GPSLatitudeRef={ref}")
            args.append(f"-EXIF:GPSLatitude={value}")

        if origin_gps_longitude:
            if not longitude_valid(origin_gps_longitude):
                raise ValueError("Invalid longitude")
            value = float(origin_gps_longitude)
            ref = "W" if value < 0 else "E"
            args.append(f"-EXIF:GPSLongitudeRef={ref}")
            args.append(f"-EXIF:GPSLongitude={value}")

        if origin_city:
            args.append(f"-IPTC:City={origin_city}")
            args.append(f"-XMP-photoshop:City={origin_city}")
            args.append(f"-XMP-iptcExt:LocationShownCity={origin_city}")

        if origin_sublocation:
            args.append(f"-IPTC:Sub-location={origin_sublocation}")
            args.append(f"-XMP-iptcCore:Location={origin_sublocation}")
            args.append(f"-XMP-iptcExt:LocationShownSublocation={origin_sublocation}")

        xmp_description_parts = []
        if comments_description:
            args.append(f"-EXIF:ImageDescription={comments_description}")
            args.append(f"-IPTC:Caption-Abstract={comments_description}")
            xmp_description_parts.append(comments_description)

        if comments_user_comment or comments_auto_comment:
            comment_parts = []
            if comments_user_comment:
                comment_parts.append(comments_user_comment)
            if comments_auto_comment:
                comment_parts.append(comments_auto_comment)
            comment = "\n\n".join(comment_parts)
            args.append(f"-EXIF:UserComment={to_ascii(comment)}")
            xmp_description_parts.append(comment)

        if xmp_description_parts:
            args.append(f"-XMP-dc:Description={'\n\n'.join(xmp_description_parts)}")

        if camera_make:
            args.append(f"-EXIF:Make={camera_make}")

        if camera_model:
            args.append(f"-EXIF:Model={camera_model}")

        if camera_serial:
            args.append(f"-EXIF:CameraSerialNumber={camera_serial}")

        lens_model_parts = []
        if lens_make:
            args.append(f"-EXIF:LensMake={lens_make}")
            lens_model_parts.append(lens_make)

        if lens_model:
            lens_model_parts.append(lens_model)
            args.append(f"-EXIF:LensModel={' '.join(lens_model_parts)}")

        if lens_serial:
            args.append(f"-EXIF:LensSerialNumber={lens_serial}")

        if lens_focal_length:
            if not focal_length_valid(lens_focal_length):
                raise ValueError("Invalid focal length")

            focal_length_values = parse_focal_length(lens_focal_length)
            args.append(f"-EXIF:FocalLength={focal_length_values[0]}")

            if camera_crop:
                try:
                    camera_crop_value = float(camera_crop)
                except ValueError as err:
                    raise ValueError("Cannot parse camera crop to float") from err

                effective_fl = focal_length_values[0] * camera_crop_value
                args.append(f"-EXIF:FocalLengthIn35mmFormat={round(effective_fl)}")

        if exposure_iso:
            if not iso_valid(exposure_iso):
                raise ValueError("Invalid ISO value")
            args.append(f"-EXIF:ISO={exposure_iso}")

        if exposure_aperture:
            if not aperture_valid(exposure_aperture):
                raise ValueError("Invalid Aperture value")
            args.append(f"-EXIF:FNumber={float(exposure_aperture)}")

        if exposure_shutter_speed:
            if not shutter_speed_valid(exposure_shutter_speed):
                raise ValueError("Invalid Shutter speed value")
            _, ss_fraction = parse_shutter_speed(exposure_shutter_speed)
            args.append(f"-EXIF:ExposureTime={ss_fraction}")

        if exposure_flash:
            if exposure_flash not in FLASH_VALUES:
                raise ValueError("Invalid flash value")
            args.append(f"-EXIF:Flash={exposure_flash}")

        if other_resolution:
            if not resolution_valid(other_resolution):
                raise ValueError("Invalid resolution value")
            resolution = float(other_resolution)
            args.append(f"-EXIF:XResolution={float(resolution)}")
            args.append(f"-EXIF:YResolution={float(resolution)}")
            args.append("-EXIF:ResolutionUnit#=2")

        if other_tags:
            tags = other_tags.strip().split(",")
            for tag in tags:
                args.append(tag)

        args.extend(images)

        return self._run_exiftool(args, _parse_result_standard).info

    def _remove_metadata(self, images: Sequence[str], tags: Sequence[str]) -> str:
        if not images:
            raise ValueError("No files provided for metadata removal.")

        if not tags:
            raise ValueError("No metadata tags specified for removal.")

        args = [
            self._binary,
        ]

        for tag in tags:
            args.append(f"-{tag}=")

        args.extend(images)

        return self._run_exiftool(args, _parse_result_standard).info

    def _get_metadata(self, images: Sequence[str]) -> str:
        if not images:
            raise ValueError("No files provided for metadata viewing.")

        args = [
            self._binary,
            "-G1",
            "-json",
            "-api",
            "structformat=jsonq",
            "-a",
            "-s",
            "-q",
        ]
        args.extend(images)

        return self._run_exiftool(args, _parse_result_standard).stdout

    def _export_metadata(self, images: Sequence[str]) -> RunResult:
        if not images:
            raise ValueError("No files provided for metadata export.")

        args = [
            self._binary,
            "-G",
            "-json",
            "-api",
            "structformat=jsonq",
            "--icc_profile:all",
        ]
        args.extend(images)

        return self._run_exiftool(args, _parse_result_export)

    def _import_metadata(self, images: Sequence[str], input_file: Path) -> str:
        if not images:
            raise ValueError("No files provided for metadata import.")

        args = [
            self._binary,
            f"-json={str(input_file)}",
        ]
        args.extend(images)

        return self._run_exiftool(args, _parse_result_import).info

    def _run_exiftool(
        self,
        arguments: Sequence[str],
        response_parser: Callable[[subprocess.CompletedProcess[str]], RunResult],
    ) -> RunResult:
        try:
            result = response_parser(
                subprocess.run(arguments, capture_output=True, text=True)
            )
            if result.returncode != 0:
                raise RuntimeError(f"ExifTool error: {result.stderr}")
        except FileNotFoundError:
            raise RuntimeError(f"ExifTool not found: {self._binary}")

        return result

    def _get_country_code(self, country: str) -> tuple[str, str, str]:
        for name, code2, code3 in COUNTRIES:
            if name == country:
                return name, code2, code3

        return country, "", ""


def _parse_result_standard(result: subprocess.CompletedProcess[str]) -> RunResult:
    return RunResult(
        result.returncode,
        result.stdout.strip(),
        result.stderr.strip(),
        result.stdout.strip(),
    )


def _parse_result_export(result: subprocess.CompletedProcess[str]) -> RunResult:
    return RunResult(
        result.returncode,
        result.stdout.strip(),
        result.stderr.strip(),
        result.stderr.strip(),
    )


def _parse_result_import(result: subprocess.CompletedProcess[str]) -> RunResult:
    if result.returncode != 0:
        return RunResult(
            result.returncode,
            result.stdout.strip(),
            result.stderr.strip(),
            result.stdout.strip(),
        )

    stderr = [
        part for part in [part.strip() for part in result.stderr.split("\n")] if part
    ]
    if len(stderr) > 1:
        return RunResult(1, "", result.stderr.strip(), "")
    else:
        info = stderr[-1] if stderr else ""
        return RunResult(result.returncode, info, "", info)
