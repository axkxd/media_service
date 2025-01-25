from environs import Env


env = Env()
env.read_env()


DATABASE_URL = env.str("DATABASE_URL")

TEST_DB_URL = env.str("TEST_DB_URL")

CLOUD_URL = env.str("CLOUD_URL")
