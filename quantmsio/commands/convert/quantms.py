from pathlib import Path
import os
from typing import Optional
import sys

import click
from quantmsio.core.project import create_uuid_filename
from quantmsio.commands.convert.feature import convert_feature
from quantmsio.commands.convert.psm import convert_psm


def find_file(directory: str, pattern: str) -> Optional[Path]:
    """Find first file matching pattern in directory."""
    path = Path(directory)
    files = list(path.rglob(pattern))
    return files[0] if files else None


def get_project_prefix(sdrf_file: Path) -> str:
    """Extract project prefix from SDRF filename (e.g. 'PXD000865' from 'PXD000865.sdrf.tsv')."""
    filename = sdrf_file.name
    # Remove .sdrf.tsv and any variations like _openms_design.sdrf.tsv
    prefix = filename.split(".sdrf")[0].split("_openms")[0]
    return prefix


def check_dir(folder_path: str) -> None:
    """Create directory if it doesn't exist."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def quantmsio_workflow(
    base_folder: str, output_folder: str, project_accession: str, quantms_version: Optional[str] = None, quantmsio_version: Optional[str] = None
) -> None:
    """Convert quantms output to quantms.io format.

    Expected structure:
    base_folder/
        quant_tables/
            *.mzTab
            *msstats_in.csv
        sdrf/
            *.sdrf.tsv
        spectra/
            mzml_statistics/
    """
    print("\n=== Starting quantms.io Conversion Workflow ===")

    # Setup paths
    print("\n📁 Setting up input paths...")
    quant_tables = Path(base_folder) / "quant_tables"
    sdrf_dir = Path(base_folder) / "sdrf"
    spectra_dir = Path(base_folder) / "spectra"

    # Find required files
    print("🔍 Searching for required files...")
    mztab_file = find_file(quant_tables, "*.mzTab")
    msstats_file = find_file(quant_tables, "*msstats_in.csv")
    sdrf_file = find_file(sdrf_dir, "*.sdrf.tsv")
    mzml_stats = spectra_dir / "mzml_statistics"

    if not all([mztab_file, msstats_file, sdrf_file, mzml_stats.exists()]):
        missing = []
        if not mztab_file:
            missing.append("mzTab file")
        if not msstats_file:
            missing.append("MSstats input file")
        if not sdrf_file:
            missing.append("SDRF file")
        if not mzml_stats.exists():
            missing.append("mzML statistics")
        raise click.UsageError(f"❌ Missing required files: {', '.join(missing)}")

    print("\n📄 Found input files:")
    print(f"   - mzTab file: {mztab_file}")
    print(f"   - MSstats file: {msstats_file}")
    print(f"   - SDRF file: {sdrf_file}")
    print(f"   - mzML statistics: {mzml_stats}")

    print(f"\n🏷️  Using project accession: {project_accession}")

    # Create output directory
    output_folder_path = Path(output_folder).resolve()  # Get absolute path
    check_dir(str(output_folder_path))
    print(f"\n📂 Output directory: {output_folder_path}")

    # Initialize project
    print("\n=== Initializing Project ===")
    try:
        project_handler = check_directory(str(output_folder_path), project_accession)
        project_handler.populate_from_pride_archive()
        project_handler.populate_from_sdrf(str(sdrf_file))
        project_handler.add_quantms_version(quantmsio_version=quantmsio_version)
        project_handler.add_software_provider(
            sortware_name="quantms",
            sortware_version=quantms_version
        )
        project_handler.add_sdrf_file(
            sdrf_file_path=str(sdrf_file),
            output_folder=str(output_folder_path),
            delete_existing=True,
        )
        print("✅ Project initialization completed successfully")
    except Exception as e:
        print(f"❌ Project initialization failed: {str(e)}", file=sys.stderr)
        return

    try:
        # Convert features
        print("\n=== Starting Feature Conversion ===")
        convert_feature(
            sdrf_file=sdrf_file,
            msstats_file=msstats_file,
            mztab_file=mztab_file,
            file_num=30,
            output_folder=output_folder_path,
            duckdb_max_memory="64GB",
            output_prefix=project_accession,
            verbose=True,  # Enable verbose logging
        )
        print("✅ Feature conversion completed successfully")
    except Exception as e:
        print(f"❌ Feature conversion failed: {str(e)}", file=sys.stderr)

    try:
        # Convert PSMs
        print("\n=== Starting PSM Conversion ===")
        convert_psm(
            mztab_file=mztab_file,
            output_folder=output_folder_path,
            output_prefix=project_accession,
            verbose=True,  # Enable verbose logging
        )
        print("✅ PSM conversion completed successfully")
    except Exception as e:
        print(f"❌ PSM conversion failed: {str(e)}", file=sys.stderr)

    print("\n=== Conversion Workflow Complete ===\n")


@click.command(
    "quantms",
    short_help="Convert quantms project output to quantms.io format",
)
@click.option(
    "--quantms-dir",
    help="The quantms project directory containing quant_tables, sdrf, and spectra subdirectories",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.option(
    "--output-dir",
    help="Output directory for quantms.io files (defaults to 'quantms.io' in parent directory)",
    required=False,
    type=click.Path(file_okay=False, path_type=Path),
)
@click.option(
    "--project-accession",
    help="PRIDE project accession (e.g. 'PXD000865')",
    required=True,
    type=str,
)
@click.option(
    "--quantms-version",
    help="Version of quantms used to generate the data",
    required=True,
    type=str,
)
@click.option(
    "--quantmsio-version",
    help="Version of quantms.io used for conversion",
    required=True,
    type=str,
)
def convert_quantms_project_cmd(
    quantms_dir: Path,
    output_dir: Optional[Path] = None,
    project_accession: str = None,
    quantms_version: str = None,
    quantmsio_version: str = None,
) -> None:
    """Convert a quantms project output to quantms.io format.

    The script expects a quantms output directory with:
    - quant_tables/ containing mzTab and MSstats files
    - sdrf/ containing SDRF files
    - spectra/ containing mzML statistics
    """
    # Default output to sibling quantms.io directory
    if not output_dir:
        output_dir = str(quantms_dir.parent / "quantms.io")

    quantmsio_workflow(str(quantms_dir), output_dir, project_accession, quantms_version, quantmsio_version)


# @click.command(
#     "psm",
#     short_help="Convert quantms PSMs from psm.tsv to parquet file in quantms.io",
# )
# @click.option(
#     "--psm-file",
#     help="the psm.tsv file, this will be used to extract the peptide information",
#     required=True,
# )
# @click.option(
#     "--output-folder",
#     help="Folder where the parquet file will be generated",
#     required=True,
# )
# @click.option(
#     "--output-prefix",
#     help="Prefix of the parquet file needed to generate the file name",
#     required=False,
# )
# def convert_quantms_psm(
#     psm_file: str,
#     output_folder: str,
#     output_prefix: str,
# ):
#     """
#     :param psm_file: the psm.tsv file, this will be used to extract the peptide information
#     :param output_folder: Folder where the parquet file will be generated
#     :param output_prefix: Prefix of the Json file needed to generate the file name
#     """

#     if psm_file is None or output_folder is None:
#         raise click.UsageError("Please provide all the required parameters")

#     if not output_prefix:
#         output_prefix = "psm"

#     output_path = (
#         output_folder + "/" + create_uuid_filename(output_prefix, ".psm.parquet")
#     )
#     quantms_psm = QuantmsPSM(psm_file)
#     quantms_psm.write_psm_to_file(output_path)


# @click.command(
#     "feature",
#     short_help="Convert quantms feature from evidence.txt to parquet file in quantms.io",
# )
# @click.option(
#     "--feature-file",
#     help="the feature.tsv file, this will be used to extract the peptide information",
#     required=True,
# )
# @click.option(
#     "--output-folder",
#     help="Folder where the parquet file will be generated",
#     required=True,
# )
# @click.option(
#     "--output-prefix",
#     help="Prefix of the parquet file needed to generate the file name",
#     required=False,
# )
# def convert_quantms_feature(
#     feature_file: str,
#     output_folder: str,
#     output_prefix: str,
# ):
#     if feature_file is None or output_folder is None:
#         raise click.UsageError("Please provide all the required parameters")

#     if not output_prefix:
#         output_prefix = "feature"

#     filename = create_uuid_filename(output_prefix, ".feature.parquet")
#     output_path = output_folder + "/" + filename
#     quantms_feature = QuantmsFeature(feature_file)
#     quantms_feature.write_feature_to_file(output_path)
