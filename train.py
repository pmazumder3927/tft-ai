import gym

from stable_baselines3 import PPO

from env import TFTEnv

env = TFTEnv.TFTEnv()

model = PPO('MlpPolicy', env, verbose=1)
model.learn(total_timesteps=24000)

obs = env.reset()
for i in range(1000):
    action, _state = model.predict(obs)
    obs, reward, done, info = env.step(action)
    env.render()
    if done:
        obs = env.reset()
