import os

from platformdirs import PlatformDirs


dirs = PlatformDirs(appname="tdx-combine")
CONFIG_PATH = os.path.join(dirs.user_data_dir, "config.yaml")
DATABASE_PATH = os.path.join(dirs.user_data_dir, "model.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH}"
