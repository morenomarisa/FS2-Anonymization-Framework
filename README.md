# FS²: A Framework for Anonymization of Unstructured Portuguese Text

This repository contains the source code, datasets, notebooks, and experimental artifacts of the **FS² framework**, a hybrid approach for anonymizing personal data in unstructured Brazilian Portuguese text.

The framework is composed of two complementary modules:

- **Module I – Regex-Based Anonymization**: responsible for identifying and anonymizing structured personal data such as phone numbers, e-mail addresses, CPF/CNPJ identifiers, and banking information through regular expressions and specialized tokenizers.
- **Module II – ReName Model**: responsible for identifying and correcting personal-name recognition in unstructured text using contextual and lexical information.

Together, these modules provide support for the anonymization of sensitive information in textual datasets while preserving data utility.

## Scientific Publications

The development of the framework is documented in the following publications:

### Module I

Antonio, S. G. R. D.; Giestas, F. C.; Santos, F. S.; Silva, E. P.; Torres, R. H. (2025).

*Proposta de Ferramenta para Otimizar a Extração de Dados em Boletins de Ocorrência: Um Estudo Piloto na Diretoria Estadual de Combate a Crimes Cibernéticos da Polícia Civil do Estado do Pará.*

Abakós, 13(1).

### Module II

de Andrade, M.; Lima, K.; Cardoso, B.; Lima, J.; Torres, R.; Neto, N. (2025).

*Name Pattern Recognition: A Model Proposal Applied to the Anonymization of Unstructured Data.*

International Conference on Computational Science and Its Applications (ICCSA 2025), Springer.

## Datasets

### Police Reports Dataset

The framework was originally developed and evaluated using a corpus of Brazilian police reports (BOs) obtained through a cooperation agreement with the Cybercrime Division of the Civil Police of Pará State, Brazil.

Due to privacy and legal restrictions, this dataset is not publicly distributed.

### AnonyMED-BR Dataset

Experiment II evaluates the framework in a different domain using the public **AnonyMED-BR** corpus:

Schiezaro, M.; Rosa, G.; Campos, B. A. G.; Pedrini, H. (2025).

*Guardians of the Data: NER and LLMs for Effective Medical Record Anonymization in Brazilian Portuguese.*

Frontiers in Public Health, 13.

The AnonyMED-BR dataset is included in this repository to ensure reproducibility of Experiment II.

## Repository Structure

```text
FS2-Anonymization-Framework/
│
├── Module_I_Regex/
│   ├── data/
│   ├── outputs/
│   ├── AnonCustomizado/
│   └── ExperimentoII_moduloI_Regex_AnonyMED_Br.ipynb
│
├── Module_II_ReNameModel/
│   └── ...
│
├── README.md
├── requirements.txt
└── .gitignore
```

## Experiment II – Cross-Domain Validation

The notebook:

```text
Module_I_Regex/ExperimentoII_moduloI_Regex_AnonyMED_Br.ipynb
```

reproduces the cross-domain validation experiment presented in the manuscript.

This experiment evaluates the Regex module using medical records from the AnonyMED-BR corpus.

The evaluated entities are:

- Phone Numbers
- E-mail Addresses

Personal names are annotated in the corpus but are addressed by **Module II (ReName Model)** and therefore are not part of the Regex evaluation.

## Reproducing the Experiments

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Then open the desired notebook and execute all cells sequentially.

## Environment

The experiments were executed using:

- Python 3.11
- pandas
- numpy
- matplotlib
- scikit-learn
- openpyxl

## Reproducibility

All code, datasets, notebooks, and scripts required to reproduce the reported results are provided in this repository.

The repository was organized to allow independent reproduction of both Module I and Module II experiments.