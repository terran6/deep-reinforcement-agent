from unityagents import UnityEnvironment
from dqn import dqn_agent, dqn_algo
import numpy as np
import time
import sys
import os


def load_env():
    """
    This function initializes the UnityEnviornment based on the running
    operating system.

    Returns:
        env: A UnityEnvironment used for Agent evaluation and training.
    """

    # Designate unity environment directory.
    env_loc = r'./unity_env'

    # Set path for unity environment based on operating system.
    if sys.platform == 'linux':
        p = os.path.join(env_loc, r'Banana_Linux/Banana.x86_64')
    elif sys.platform == 'darwin':
        p = os.path.join(env_loc, r'Banana')
    else:
        p = os.path.join(env_loc, r'Banana_Windows_x86_64/Banana.exe')

    # Initialize UnityEnvironment env with executable located in path p.
    env = UnityEnvironment(file_name=p)

    # Extract state dimensionality from env.
    brain_name = env.brain_names[0]
    env_info = env.reset(train_mode=True)[brain_name]
    obs = env_info.vector_observations[0].copy()
    state = np.expand_dims(obs, 0)
    state_size = state.shape

    # Extract action dimensionality from env.
    brain = env.brains[brain_name]
    action_size = brain.vector_action_space_size

    return env, state_size, action_size


def create_agent(state_size, action_size, buffer_size=int(1e5), batch_size=64,
                 gamma=0.99, tau=1e-3, lr=5e-4, update_frequency=4, duel=True):
    """
    This function creates the agent with specified parameters for training.

    Arguments:
        state_size: An integer count of dimensions for each state.
        action_size: An integer count of dimensions for each action.
        buffer_size: An integer for replay buffer size.
        batch_size: An integer for minibatch size.
        gamma: A float designating the discount factor.
        tau: A float designating multiplication factor for soft update of
            target parameters.
        lr: A float designating the learning rate of the optimizer.
        update_frequency: An integer designating the step frequency of
            updating target network parameters.
        duel: A boolean which specifies the use of either Dueling Q Networks
            or traditional Q Networks for training.

    Returns:
        agent: An Agent object used for training.
    """

    # Initialize Agent hyperparameters.
    agent_hparams = dqn_agent.AgentHyperparams(
        buffer_size=buffer_size,
        batch_size=batch_size,
        gamma=gamma,
        tau=tau,
        lr=lr,
        update_frequency=update_frequency,
        duel=duel
    )

    # Create agent for training.
    agent = dqn_agent.Agent(
        state_size=state_size,
        action_size=action_size,
        seed=0,
        agent_hparams=agent_hparams
    )

    return agent


def train_agent(agent, env, n_episodes=1000, max_t=1000, eps_start=1.0,
                eps_end=0.01, eps_decay=0.995, save_dir=r'./final_model'):
    """
    This function carries out the training process for the designated agent.

    Arguments:
        agent: An Agent object used for training.
        env: A UnityEnvironment used for Agent evaluation and training.
        n_episodes: An integer for maximum number of training episodes.
        max_t: An integer for maximum number of timesteps per episode.
        eps_start: A float for the starting value of epsilon, for
            epsilon-greedy action selection.
        eps_end: A float to set the minimum value of epsilon.
        eps_decay: A float multiplicative factor (per episode) for decreasing
            epsilon.
        save_dir: Path designating directory to save resulting files.
    """

    # Create DQNTrainer object to train agent.
    trainer = dqn_algo.DQNTrainer(
        agent=agent,
        env=env,
        max_t=max_t,
        eps_start=eps_start,
        eps_end=eps_end,
        eps_decay=eps_decay,
        save_dir=save_dir
    )

    # Train the agent with trainer object.
    t_start = time.time()
    print('Starting training...')
    trainer.train(n_episodes=n_episodes)
    print('\nFinished training, closing env.')
    env.close()
    t_end = time.time()

    # Notify of time needed to train agent to solve environment.
    delta = t_end - t_start
    minutes = delta / 60
    print(f'Training took {minutes:.1f} minutes.')

    # Save successful network parameters.
    print('Saving trainer...')
    trainer.save()
    print('Done.')


if __name__ == '__main__':

    # Initialize environment and extract action and state dimensions.
    env, state_size, action_size = load_env()

    # Create agent used for training.
    agent = create_agent(state_size, action_size, duel=True)

    # Train agent in specified environment!
    train_agent(agent, env)