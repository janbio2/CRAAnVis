import glob
import json
from typing import Dict, Any, List


def read_newick(file_path) -> str:
    """
    Read Newick formatted tree file.
    :return: string representing the Newick tree
    """
    try:
        with open(file_path, 'r') as file:
            newick_tree = file.read()
            if newick_tree.endswith('"'):
                newick_tree = newick_tree[:-1]
            if newick_tree.startswith('"'):
                newick_tree = newick_tree[1:]
        return newick_tree
    except FileNotFoundError:
        print("Newick tree file not found.")
        return ""


def read_rec_spacers(file_path) -> Dict:
    """
    Read rec_spacers.json file into a DataFrame.
    :return: DataFrame representing rec_spacers
    """
    try:
        with open(file_path, 'r') as file:
            rec_spacers = json.load(file)
        return rec_spacers
    except FileNotFoundError:
        print("rec_spacers.json file not found.")
        return {}


def read_top_order(file_path) -> list:
    """
    Read top_order.json file.
    :return: list representing top_order
    """
    try:
        with open(file_path, 'r') as file:
            top_order = json.load(file)
        return top_order
    except FileNotFoundError:
        print("top_order.json file not found.")
        return []


def read_spacer_names_to_numbers(file_path) -> Dict[str, int]:
    """
    Read spacer_names_to_numbers.json file.
    :return: dict mapping spacer names to numbers
    """
    try:
        with open(file_path, 'r') as file:
            spacer_names_to_numbers = json.load(file)
        return spacer_names_to_numbers
    except FileNotFoundError:
        print("spacer_names_to_numbers.json file not found.")
        return {}


def read_rec_gains_losses(file_path) -> Dict[str, Dict[str, List[str]]]:
    """
    Read rec_gains_losses.json file into a dictionary.
    :return: dictionary representing rec_gains_losses
    """
    try:
        with open(file_path, 'r') as file:
            rec_gains_losses = json.load(file)
        return rec_gains_losses
    except FileNotFoundError:
        print("rec_gains_losses.json file not found.")
        return {}


def read_other_events(file_path) -> Dict[str, Dict[str, List[str]]]:
    """
    Read other_events.json file.
    :return: dict representing other_events
    """
    print(file_path)
    try:
        with open(file_path, 'r') as file:
            other_events = json.load(file)
        return other_events
    except FileNotFoundError:
        print("other_events.json file not found.")
        return {}


def read_json_metadata(file_path) -> Dict[str, Any]:
    """
    Read metadata.json file.
    :return: dict representing metadata
    """
    try:
        with open(file_path, 'r') as file:
            metadata = json.load(file)
            for key, value in metadata.items():
                metadata[key] = deserialize_metadata(value)
        return metadata
    except FileNotFoundError:
        print("metadata.json file not found.")
        return {}


def deserialize_item(item):
    value_type = item['type']
    try:
        if value_type == 'int':
            return int(item['value'])
        elif value_type == 'float':
            return float(item['value'])
        elif value_type == 'str':
            return str(item['value'])
        elif value_type == 'list':
            return [deserialize_item(i) for i in item['value']]
        else:
            raise ValueError(f"Unexpected type {value_type}")
    except ValueError as e:
        print(f"Error deserializing item: {e}")
        return None


def deserialize_metadata(serialized_data):
    deserialized_data = {}
    for key, item in serialized_data.items():
        deserialized_data[key] = deserialize_item(item)
    return deserialized_data


def read_all_folder_data(folder_path: str) -> Dict[str, Any]:
    """
    Runs all the read functions and stores their output in a dictionary.
    :param folder_path: string representing the directory path
    :return: dictionary storing the output of all read functions
    """
    file_paths = find_file_paths(folder_path,
                                 [".nwk",
                                  "_rec_spacers.json",
                                  "_top_order.json",
                                  "_spacer_names_to_numbers.json",
                                  "_rec_gains_losses.json",
                                  "_other_events.json",
                                  "_metadata.json"])

    data = {'newick': read_newick(file_paths['.nwk']),
            'rec_spacers': read_rec_spacers(file_paths['_rec_spacers.json']),
            'top_order': read_top_order(file_paths['_top_order.json']),
            'spacer_names_to_numbers': read_spacer_names_to_numbers(file_paths['_spacer_names_to_numbers.json']),
            'rec_gains_losses': read_rec_gains_losses(file_paths['_rec_gains_losses.json']),
            'other_events': read_other_events(file_paths['_other_events.json'])}

    if '_metadata.json' in file_paths:
        data['metadata'] = read_json_metadata(file_paths['_metadata.json'])

    return data


def find_file_paths(folder_path, file_types):
    """
    Find all files in a folder with a certain file type.
    :param folder_path: string representing the directory path
    :param file_types: list of strings representing file types
    :return: dict representing filetypes with corresponding file paths
    """
    if not folder_path.endswith('/'):
        folder_path += '/'

    file_paths = {}
    for file_type in file_types:
        file_path = glob.glob(folder_path + '*' + file_type)
        if not file_path:
            print(f"No {file_type} files found.")
            continue
        file_paths[file_type] = file_path[0]

    return file_paths
