import click

from quantmsio.core.de import DifferentialExpressionHandler
from quantmsio.utils.file_utils import extract_protein_list


@click.command(
    "differential",
    short_help="Convert a MSstats differential file into a quantms.io file format",
)
@click.option("--msstats_file", help="MSstats differential file", required=True)
@click.option(
    "--sdrf_file",
    help="the SDRF file needed to extract some of the metadata",
    required=True,
)
@click.option(
    "--project_file",
    help="quantms.io project file",
    required=False,
)
@click.option(
    "--fdr_threshold",
    help="FDR threshold to use to filter the results",
    required=False,
    default="0.05",
)
@click.option(
    "--protein_file",
    help="Protein file that meets specific requirements",
    required=False,
)
@click.option(
    "--output_folder", help="Folder to generate the df expression file.", required=True
)
@click.option(
    "--output_prefix_file", help="Prefix of the df expression file", required=False
)
@click.option(
    "--delete_existing", help="Delete existing files in the output folder", is_flag=True
)
def convert_msstats_differential(
    msstats_file: str,
    sdrf_file: str,
    project_file: str,
    protein_file: str,
    fdr_threshold: float,
    output_folder: str,
    output_prefix_file: str,
    delete_existing: bool = True,
):

    if msstats_file is None or sdrf_file is None or output_folder is None:
        raise click.UsageError("Please provide all the required parameters")
    protein_list = extract_protein_list(protein_file) if protein_file else None
    protein_str = "|".join(protein_list) if protein_list else None
    de_handler = DifferentialExpressionHandler()
    if project_file:
        de_handler.load_project_file(project_file)
    de_handler.load_msstats_file(msstats_file, protein_str)
    de_handler.load_sdrf_file(sdrf_file)
    de_handler.set_fdr_threshold(fdr_threshold=fdr_threshold)
    de_handler.convert_msstats_to_quantms(
        output_folder=output_folder,
        output_file_prefix=output_prefix_file,
        delete_existing=delete_existing,
    )
