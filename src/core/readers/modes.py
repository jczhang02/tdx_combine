import os
from typing import List

import aiofiles


async def get_modes(path: str | os.PathLike[str]) -> List[str]:
    """Function with provides a list contains block code that needed
    to be passed to calculate.

    Parameters
    ----------
    path : str | os.PathLike[str]
        Path of user customized mode file, which is always passed from fronted flet
        controls.

    Returns
    -------
    List[str]
        A list contains block codes.

    """
    blocks: List[str] = []
    async with aiofiles.open(path, "r", encoding="gbk") as f:
        async for line in f:
            line = line.strip()
            if line and line.isdigit():
                blocks.append(line)

    return blocks
