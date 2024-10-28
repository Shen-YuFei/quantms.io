import pyarrow as pa

PEPTIDE_FIELDS = [
    pa.field(
        "sequence",
        pa.string(),
        metadata={"description": "The peptide’s sequence corresponding to the PSM"},
    ),
    pa.field(
        "peptidoform",
        pa.string(),
        metadata={"description": "Peptide sequence with modifications: Read the specification for more details"},
    ),
    pa.field(
        "modifications",
        pa.list_(
            pa.struct(
                [
                    ("modification_name", pa.string()),
                    (
                        "fields",
                        pa.list_(pa.struct([("position", pa.int32()), ("localization_probability", pa.float32())])),
                    ),
                ]
            )
        ),
        metadata={
            "description": "List of alternative site probabilities for the modification format: read the specification for more details"
        },
    ),
    pa.field(
        "precursor_charge",
        pa.int32(),
        metadata={"description": "charge state of the feature"},
    ),
    pa.field(
        "posterior_error_probability",
        pa.float32(),
        metadata={"description": "Posterior error probability for the given peptide spectrum match"},
    ),
    pa.field(
        "is_decoy",
        pa.int32(),
        metadata={"description": "Decoy indicator, 1 if the PSM is a decoy, 0 target"},
    ),
    pa.field(
        "calculated_mz",
        pa.float32(),
        metadata={
            "description": "Theoretical peptide mass-to-charge ratio based on identified sequence and modifications"
        },
    ),
    pa.field(
        "observed_mz",
        pa.float32(),
        metadata={"description": "Experimental peptide mass-to-charge ratio of identified peptide (in Da)"},
    ),
    pa.field(
        "additional_scores",
        pa.list_(pa.struct([("score_name", pa.string()), ("score_value", pa.float32())])),
        metadata={"description": "List of structures, each structure contains two fields: name and value"},
    ),
    pa.field(
        "mp_accessions",
        pa.list_(pa.string()),
        metadata={"description": "Protein accessions of all the proteins that the peptide maps to"},
    ),
    pa.field(
        "predicted_rt",
        pa.float32(),
        metadata={"description": "Predicted retention time of the peptide (in seconds)"},
    ),
    pa.field(
        "reference_file_name",
        pa.string(),
        metadata={"description": "Spectrum file name with no path information and not including the file extension"},
    ),
    pa.field(
        "cv_params",
        pa.list_(pa.struct([("cv_name", pa.string()), ("cv_value", pa.string())])),
        metadata={"description": "Optional list of CV parameters for additional metadata"},
    ),
    pa.field(
        "scan",
        pa.string(),
        metadata={"description": "Scan index (number of nativeId) of the spectrum identified"},
    ),
    pa.field(
        "rt",
        pa.float32(),
        metadata={"description": "MS2 scan’s precursor retention time (in seconds)"},
    ),
    pa.field(
        "ion_mobility",
        pa.float32(),
        metadata={"description": "Ion mobility value for the precursor ion"},
    ),
]

PSM_UNIQUE_FIELDS = [
    pa.field(
        "number_peaks",
        pa.int32(),
        metadata={"description": "Number of peaks in the spectrum used for the peptide spectrum match"},
    ),
    pa.field(
        "mz_array",
        pa.list_(pa.float32()),
        metadata={"description": "Array of m/z values for the spectrum used for the peptide spectrum match"},
    ),
    pa.field(
        "intensity_array",
        pa.list_(pa.float32()),
        metadata={"description": "Array of intensity values for the spectrum used for the peptide spectrum match"},
    ),
]

FEATURE_UNIQUE_FIELDS = [
    pa.field(
        "intensities",
        pa.list_(pa.struct([("sample_accession", pa.string()), ("channel", pa.string()), ("intensity", pa.float32())])),
        metadata={"description": "The intensity-based abundance of the peptide in the sample"},
    ),
    pa.field(
        "additional_intensities",
        pa.list_(
            pa.struct(
                [
                    ("sample_accession", pa.string()),
                    ("channel", pa.string()),
                    ("additional_intensity", pa.list_(pa.struct([("name", pa.string()), ("value", pa.float32())]))),
                ]
            )
        ),
        metadata={
            "description": "Apart from the raw intensity, multiple intensity values can be provided as key-values pairs, for example, normalized intensity."
        },
    ),
    pa.field(
        "pg_accessions",
        pa.list_(pa.string()),
        metadata={"description": "Protein group accessions of all the proteins that the peptide maps to"},
    ),
    pa.field(
        "anchor_protein",
        pa.string(),
        metadata={"description": "One protein accession that represents the protein group"},
    ),
    pa.field(
        "unique",
        pa.int32(),
        metadata={
            "description": "Unique peptide indicator, if the peptide maps to a single protein, the value is 1, otherwise 0"
        },
    ),
    pa.field(
        "pg_global_qvalue",
        pa.float32(),
        metadata={"description": "Global q-value of the protein group at the experiment level"},
    ),
    pa.field(
        "start_ion_mobility",
        pa.float32(),
        metadata={"description": "start ion mobility value for the precursor ion"},
    ),
    pa.field(
        "stop_ion_mobility",
        pa.float32(),
        metadata={"description": "stop ion mobility value for the precursor ion"},
    ),
    pa.field(
        "gg_accessions",
        pa.list_(pa.string()),
        metadata={"description": "Gene accessions, as string array"},
    ),
    pa.field(
        "gg_names",
        pa.list_(pa.string()),
        metadata={"description": "Gene names, as string array"},
    ),
    pa.field(
        "scan_reference_file_name",
        pa.string(),
        metadata={"description": "The reference file containing the best psm that identified the feature."},
    ),
    pa.field(
        "rt_start",
        pa.float32(),
        metadata={"description": "Start of the retention time window for feature"},
    ),
    pa.field(
        "rt_stop",
        pa.float32(),
        metadata={"description": "End of the retention time window for feature"},
    ),
]


PG_MATRIX = [
    pa.field(
        "pg_accessions",
        pa.list_(pa.string()),
        metadata={"description": "Protein group accessions of all the proteins that the peptide maps to"},
    ),
    pa.field(
        "gg_names",
        pa.list_(pa.string()),
        metadata={"description": "Gene names, as string array"},
    ),
    pa.field(
        "quantmsio_version",
        pa.string(),
        metadata={"description": "The version of quantms.io"},
    ),
    pa.field(
        "first_protein_description",
        pa.string(),
        metadata={"description": "About the specific information of the first protein"},
    ),
    pa.field(
        "reference_file_name",
        pa.string(),
        metadata={"description": "The reference file name that contains the feature"},
    ),
    pa.field(
        "peptides",
        pa.list_(pa.struct([("name", pa.string()), ("value", pa.string())])),
        metadata={"description": "The count of peptides in each reference"},
    ),
    pa.field(
        "intensities",
        pa.list_(pa.struct([("name", pa.string()), ("value", pa.float32())])),
        metadata={"description": "The total intensity of proteins in the reference"},
    ),
]


PSM_FIELDS = PEPTIDE_FIELDS + PSM_UNIQUE_FIELDS

FEATURE_FIELDS = PEPTIDE_FIELDS + FEATURE_UNIQUE_FIELDS

# pa.field(
#     "modifications",
#     pa.list_(pa.string()),
#     metadata={"description": "List of modifications as string array, easy for search and filter"},
# ),

# pa.field(
#     "consensus_support",
#     pa.float32(),
#     metadata={
#         "description": "Consensus support for the given peptide spectrum match, when multiple search engines are used"
#     },
# ),


# pa.field(
#     "rank", pa.int32(), metadata={"description": "Rank of the peptide spectrum match in the search engine output"}
# ),
# pa.field(
#     "best_id_score",
#     pa.list_(pa.struct([("name", pa.string()), ("value", pa.float32())])),
#     metadata={
#         "description": "A named score type and value representing an identification's measure of confidence or input feature"
#     },
# ),
