import os
from enum import Enum
from pathlib import Path
import re

import click
import numpy as np
import pandas as pd
from ccfcoef.family import CPU_FAMILIES, BOAVIZTA_CODENAME_TO_ARCHITECTURE_MAP

BOAVIZTA_CPU_SPEC_URL = 'https://github.com/Boavizta/boaviztapi/blob/main/boaviztapi/data/crowdsourcing/cpu_specs.csv'

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR.joinpath('data')
OUTPUT_DIR = PROJECT_DIR.joinpath('output')


# TODO: move
rename_maps = {
    'azure': {
        'id': 'Virtual Machine',
        'vcpu': 'Instance vCPUs',
        'memory': 'Instance Memory',
        'gpu_units': 'Instance GPUs',
        'CPU.units': 'Platform Sockets',
        'CPU.core_units': 'Platform Cores',
        'CPU.name': 'Platform CPU Name',
        'CPU.threads': 'Platform Threads',
        'GPU.units': 'Platform GPU',
        'GPU.name': 'Platform GPU Name',
        'STORAGE.type': 'Platform Storage Type',
        'platform_max_vcpu': 'Platform vCPUs (highest vCPU possible)',
        'platform_max_memory': 'Platform Memory',
        'platform_max_storage_drive_quantity': 'Platform (largest instance) Storage Drive quantity',
    },
    'aws': {
        'id': 'Instance type',
        'vcpu': 'Instance vCPU',
        'memory': 'Instance Memory (in GB)',
        'gpu_units': 'Instance Number of GPU',
        'CPU.units': 'Platform Number of CPU Sockets',
        'CPU.core_units': 'Platform Cores',
        'CPU.name': 'Platform CPU Name',
        'CPU.threads': 'Platform Threads',
        'GPU.units': 'Platform GPU Quantity',
        'GPU.name': 'Platform GPU Name',
        'STORAGE.type': 'Platform Storage Type',
        'platform_max_vcpu': 'Platform Total Number of vCPU',
        'platform_max_memory': 'Platform Memory (in GB)',
        'platform_max_storage_drive_quantity': 'Platform Storage Drive Quantity',
    },
    'gcp': {
        'id': 'Machine type',
        'vcpu': 'Instance vCPUs',
        'memory': 'Instance Memory',
        'gpu_units': 'Instance GPUs',
        'CPU.units': 'Platform Sockets',
        'CPU.core_units': 'Platform Cores',
        'CPU.name': 'Platform CPU Name',
        'CPU.threads': 'Platform Threads',
        'GPU.units': 'Platform GPU',
        'GPU.name': 'Platform GPU Name',
        'STORAGE.type': 'Platform Storage Type',
        'platform_max_vcpu': 'Platform vCPUs (highest vCPU possible)',
        'platform_max_memory': 'Platform Memory',
        'platform_max_storage_drive_quantity': 'Platform (largest instance) Storage Drive quantity',
    }
}


class Provider(Enum):
    AZURE = "azure"
    GCP = "gcp"
    AWS = "aws"

class CloudProviderInstanceTypeField(Enum):
    AZURE = "Virtual Machine"
    GCP = "Machine type"
    AWS = "Instance type"


def fetch_boavizta_cpu_data():
    boavizta_df = pd.read_csv('https://raw.githubusercontent.com/Boavizta/boaviztapi/refs/heads/main/boaviztapi/data/crowdsourcing/cpu_specs.csv',
                              delimiter=',',
                              header='infer')
    # 'code_name' column contains information on architecture of corresponding cpu model
    # drop incomplete rows
    df = boavizta_df.dropna(subset=['code_name'])
    df['code_name'] = df['code_name'].astype(str)
    return df

# Derive architecture from platform cpu
def derive_cpu_microarchitecture(df, cpu_name_column, output_column='Microarchitecture'):
    model_arch_dict = {}

    for arch in CPU_FAMILIES:
        path = DATA_DIR.joinpath(f"{arch.short}.csv")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                cpus = [line.strip() for line in f]
                for model in cpus:
                    model_arch_dict[model.lower()] = arch.name
        else:
            print(f"File not found for {arch.name} at {path}")

    def get_architecture(cpu_name):
        if pd.isna(cpu_name):
            return None
        name_lower = cpu_name.lower()
        for model_substr, architecture in model_arch_dict.items():
            if model_substr in name_lower:
                return architecture
        return 'Unknown'

    df[output_column] = df[cpu_name_column].apply(get_architecture)

    return df


def derive_architecture_from_boavizta_codename(df):
    codenames = df['code_name'].unique()
    architectures = []
    for cn in codenames:
        arch = derive_architecture_from_codename(cn)
        if arch is not None:
            architectures.append(arch)
        else:
            manufacturer = df[df['code_name'] == cn]['manufacturer'].iloc[0]
            click.secho(f"WARNING: Codename '{cn}' of manufacturer {manufacturer} and corresponding architecure is not set in 'BOAVIZTA_CODENAME_TO_ARCHITECTURE_MAP'."
                        f"Must be added manually.", fg="yellow",
                        bold=True)
    return set(architectures)

# TODO: rename
def derive_architecture_from_codename(codename):
    cn = clean_codename(codename)
    architecture = BOAVIZTA_CODENAME_TO_ARCHITECTURE_MAP.get(cn)
    return architecture

def clean_codename(codename):
    cn = codename.lower().replace(' ', '')
    cn = cn.split('-')[0].strip()
    return cn

def append_boavizta_cpu_data(boavizta_df, architectures):
    existing_architectures = []
    new_architectures = []

    for arch in architectures:
        filepath = DATA_DIR.joinpath("{architecture}.csv".format(architecture=arch))

        if architecture_data_exists(filepath):
            existing_architectures.append(arch)
        else:
            new_architectures.append(arch)

    # append new cpu models from boavizta data to existing files
    for arch in existing_architectures:
        filepath = DATA_DIR.joinpath("{architecture}.csv".format(architecture=arch))
        arch_data = boavizta_df[boavizta_df['architecture'] == arch]
        append_boavizta_cpus_to_file(filepath, arch_data)

    #create new files for non existing architectures and write cpu models
    for arch in new_architectures:
        filepath = DATA_DIR.joinpath("{architecture}.csv".format(architecture=arch))
        arch_data = boavizta_df[boavizta_df['architecture'] == arch]
        write_boavizta_cpus_to_file(filepath, arch_data)
    return True

def architecture_data_exists(filepath):
    if os.path.exists(filepath):
        return True
    return False

def append_boavizta_cpus_to_file(filepath, arch_data):
    boavizta_arch_cpus = arch_data['name'].apply(clean_boavizta_cpu_name)
    # get existing cpus in file
    with open(filepath, 'r') as f:
        existing_cpus = [line.strip() for line in f.readlines()]

        # append new cpus to file
        with open(filepath, 'a') as file:
            count = 0
            for cpu in boavizta_arch_cpus:
                if cpu not in existing_cpus:
                    count += 1
                    file.writelines(f"{cpu}\n")
            print(f"Appending {count} CPUs to {filepath}")
    return True


def write_boavizta_cpus_to_file(filepath, arch_data):
    boavizta_arch_cpus = arch_data['name'].apply(clean_boavizta_cpu_name)
    with open(filepath, 'w') as file:
        click.secho(f"Writing {len(boavizta_arch_cpus)} new cpus to file: {filepath}", fg="yellow")
        for cpu in boavizta_arch_cpus:
            file.writelines(f"{cpu}\n")
    return True

def clean_boavizta_cpu_name(name):
    _name = remove_manufacturer_from_cpu_name(str(name))
    name_re = re.sub(r'\(.*?\)', '', _name)
    words = name_re.split()

    # if last word in cpu name is version number, also keep word before
    if ' v' in words[-1].lower():  # check if last word is version number
        # keep version number alongside model name
        #return ' '.join(words[-2:])
        return ' '.join(words)
    else:
        return ' '.join(words)

def remove_manufacturer_from_cpu_name(name):
    manufacturers = ['Intel', 'AMD', 'Apple', 'Annapurna Labs']
    cleaned = str(name)
    for manufacturer in manufacturers:
        pattern = rf'\b{re.escape(manufacturer)}\b'
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    result = re.sub(r'\s+', ' ', cleaned).strip()
    return result

def remove_duplicate_cpus():
    architectures = CPU_FAMILIES.copy()
    for arch in architectures:
        filepath = DATA_DIR.joinpath("{architecture}.csv".format(architecture=arch.short))
        with open(filepath, 'r') as f:
            cpus = f.readlines()
        existing_cpus = set()
        unique_cpus = []
        for cpu in cpus:
            cpu = cpu.strip()# .lower()
            if cpu not in existing_cpus:
                existing_cpus.add(cpu)
                unique_cpus.append(cpu)
        with open(filepath, 'w') as file:
            for cpu in unique_cpus:
                file.writelines(f"{cpu}\n")

def get_platform_storage_type(row):
    if pd.to_numeric(row['SSD.units']) > 0:
        return 'SSD'
    elif pd.to_numeric(row['HDD.units']) > 0:
        return 'HDD'
    else:
        return np.nan

def clean_instance_name(instance_type: str, provider: Provider):
    instance_type = instance_type.lower().strip()
    # Boavizta Azure: standard_d32as_v4 CCF: D32as v4
    if provider == Provider.AZURE:
        if instance_type.startswith("standard_"):
            instance_type = instance_type.replace("standard_", "")
        instance_type = instance_type.replace("_", " ")
    elif provider == Provider.AWS:
        pass
    elif provider == Provider.GCP:
        pass

    return instance_type

def rename_boavizta_columns_ccf(df, rename_map):
    return df.rename(columns=rename_map)

def merge_boavizta_instance_and_platform(provider: Provider):

    boavizta_instances = pd.read_csv(
        f"https://raw.githubusercontent.com/Boavizta/boaviztapi/refs/heads/main/boaviztapi/data/archetypes/cloud/{provider.value.lower()}.csv")

    boavizta_platforms = pd.read_csv(
        "https://raw.githubusercontent.com/Boavizta/boaviztapi/refs/heads/main/boaviztapi/data/archetypes/server.csv")

    # match CCF notation
    boavizta_instances['id'] = boavizta_instances['id'].apply(lambda x: clean_instance_name(x, provider))

    boavizta_platforms.rename(columns={'id': 'platform'}, inplace=True)

    merge = boavizta_instances.merge(boavizta_platforms, on='platform', how='inner')

    merge['STORAGE.type'] = merge.apply(get_platform_storage_type, axis=1)

    # remove manufacturer for cpu name matching
    merge['CPU.name'] = merge['CPU.name'].apply(remove_manufacturer_from_cpu_name)

    # Add max vCPU of platform
    merge['platform_max_vcpu'] = merge.groupby('platform')['vcpu'].transform('max')
    # Add max memory of platform
    merge['platform_max_memory'] = merge.groupby('platform')['memory'].transform('max')
    # Add platform storage info
    merge['platform_max_storage_drive_quantity'] = (merge['SSD.units'].fillna(0).astype(float) + merge['HDD.units'].fillna(0).astype(float))

    merge = rename_boavizta_columns_ccf(merge, rename_maps[provider.value])

    merge = derive_cpu_microarchitecture(merge, 'Platform CPU Name', 'Microarchitecture')

    return merge


def append_boavizta_instances(provider: Provider, boavizta_df_merged: pd.DataFrame, instance_field_name: CloudProviderInstanceTypeField):
    ccf_instances = pd.read_csv(f"https://raw.githubusercontent.com/cloud-carbon-footprint/ccf-coefficients/refs/heads/main/data/{provider.value}-instances.csv")

    keep_columns = ccf_instances.columns.intersection(boavizta_df_merged.columns)

    boavizta_lower = boavizta_df_merged[instance_field_name.value].str.lower()
    ccf_lower = ccf_instances[instance_field_name.value].str.lower()

    is_new_instance_series = ~boavizta_lower.isin(ccf_lower)
    new_instances = boavizta_df_merged[is_new_instance_series]

    if provider.value == Provider.AWS.value:
        # aws instances do not contain microarchitecture information by default
        derive_cpu_microarchitecture(ccf_instances, 'Platform CPU Name', 'Microarchitecture')
        # keep Teads energy consumption values
        keep_columns = ccf_instances.columns.intersection(new_instances.columns)

    print(f"Total Boavizta instances for {provider.value}: {len(boavizta_df_merged)}")
    print(f"New instances: {len(new_instances)}")
    return pd.concat([ccf_instances, new_instances[list(keep_columns)]], ignore_index=True)