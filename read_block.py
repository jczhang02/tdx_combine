import json
import os
import re
from typing import Dict, List, Pattern, Union

from rich import print


block_file_dir: str = "./data/infoharbor_block.dat"


def parse_stock_file(path: str | os.PathLike[str]) -> Dict[str, Dict[str, Union[str, List[str]]]] | None:
    """
    Parses a specially formatted stock block file using regular expressions.
    This function uses the unique block code as the primary key in the resulting dictionary.
    Args:
        path (str | os.PathLike[str]): The path to the file.
    Returns:
        A nested dictionary where the outer key is the block code, and the value is a
        dictionary containing the 'name' (block name) and 'stocks' (list of stock codes).
        Returns None if the file is not found or a parsing error occurs.
        Example:
        {
            '880515': {
                'name': '通达信88',
                'stocks': ['000025', '000100', ...]
            }
        }
    """
    # The main dictionary to store all parsed blocks, indexed by block code.
    blocks: Dict[str, Dict[str, Union[str, List[str]]]] = {}

    # State variables to hold data for the current block being parsed.
    cur_block_name: str = ""
    cur_block_code: str = ""
    cur_stock_list: list[str] = []
    # Pre-compile the regular expression for efficiency.
    # It matches a block header line and captures the block name.
    block_start_pattern: Pattern[str] = re.compile(r'#[a-zA-Z]+_([^,]+)')
    try:
        # Open the file with 'gbk' encoding.
        with open(path, 'r', encoding='gbk') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # 1. Check if the line is a new block header.
                match = block_start_pattern.match(line)
                if match:
                    # a. If it's a new header, first save the data of the previous block.
                    # Use the block code as the key. Ensure it's not empty.
                    if cur_block_code and cur_block_name and cur_stock_list:
                        blocks[cur_block_code] = {
                            'name': cur_block_name,
                            # 'stocks': cur_stock_list
                        }
                    # b. Parse the new block's information.
                    new_block_name = match.group(1).strip()
                    parts = line.split(',')
                    if len(parts) > 2:
                        new_block_code = parts[2].strip()
                    else:
                        new_block_code = ""
                    # c. Reset state variables for the new block.
                    cur_block_name = new_block_name
                    cur_block_code = new_block_code
                    cur_stock_list = []

                # 2. If it's not a header, it's a stock code line.
                else:
                    codes = [
                        code.strip().split('#')[-1]
                        for code in line.split(',') if code.strip()
                    ]
                    cur_stock_list.extend(codes)

            # 3. After the loop, save the very last block's data.
            # Use the block code as the key here as well.
            if cur_block_code and cur_block_name and cur_stock_list:
                blocks[cur_block_code] = {
                    'name': cur_block_name,
                    # 'stocks': cur_stock_list
                }
    except FileNotFoundError:
        print(f"Error: The file '{path}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while parsing the file: {e}")
        return None

    return blocks


parsed_blocks = parse_stock_file(block_file_dir)

print(len(parsed_blocks.keys()))


sorted_items = sorted(parsed_blocks.items(), key=lambda item: int(item[0]))
sorted_blocks = dict(sorted_items)


with open("./result.json", "w", encoding="utf-8") as json_file:
    json.dump(sorted_blocks, json_file, ensure_ascii=False)
