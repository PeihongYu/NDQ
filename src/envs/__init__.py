from functools import partial
from .multiagentenv import MultiAgentEnv
from smac_plus import StarCraft2Env, Tracker1Env, Join1Env
from smacv2.env import StarCraft2Env as StarCraft2EnvV2
from smacv2.env import StarCraftCapabilityEnvWrapper
import sys
import os


def env_fn(env, **kwargs) -> MultiAgentEnv:
	return env(**kwargs)


REGISTRY = {
	"sc2": partial(env_fn, env=StarCraft2Env),
	"tracker1": partial(env_fn, env=Tracker1Env),
	"join1": partial(env_fn, env=Join1Env),
	"sc2wrapped": partial(env_fn, env=StarCraftCapabilityEnvWrapper),
}

if sys.platform == "linux":
	os.environ.setdefault("SC2PATH",
                          "/fs/nexus-scratch/peihong/3rdparty/StarCraftII_2410")
	# os.environ.setdefault("SC2PATH", "~/StarCraftII")
	# os.environ.setdefault("SC2PATH",
	#                       os.path.join(os.getcwd(), "3rdparty", "StarCraftII"))
