import os
import numpy as np
import gym


gym.logger.set_level(40)
os.environ['GYM_CONFIG_CLASS'] = 'Example'
from gym_collision_avoidance.envs import test_cases as tc
from gym_collision_avoidance.envs import Config

def main():
    '''
    Minimum working example:
    2 agents: 1 running external policy, 1 running GA3C-CADRL
    '''

    # Create single tf session for all experiments
    import tensorflow as tf
    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
    tf.Session().__enter__()

    # Instantiate the environment
    env = gym.make("CollisionAvoidance-v0")

    # In case you want to save plots, choose the directory
    env.set_plot_save_dir(
        os.path.dirname(os.path.realpath(__file__)) + '/../../experiments/results/example/')

    # Set agent configuration (start/goal pos, radius, size, policy)
    agents = tc.get_testcase_two_agents()
    print("Pref speed", agents[1].pref_speed)
    [agent.policy.initialize_network() for agent in agents if hasattr(agent.policy, 'initialize_network')]
    env.set_agents(agents)

    obs = env.reset() # Get agents' initial observations

    # Repeatedly send actions to the environment based on agents' observations
    num_steps = 100

    set_point = np.pi/3.9
    P = 1.0
    int_err = 0.0
    err = 0.0

    for i in range(num_steps):

        # Query the external agents' policies
        # e.g., actions[0] = external_policy(dict_obs[0])
        actions = {}

        # basic test, have 1st agent go on set heading
        p_err = err
        curr = agents[0].heading_global_frame
        err = set_point - agents[0].heading_global_frame
        control = np.clip(P*err, -1, 1)/2.0 + 0.5
        actions[0] = np.array([1.0, control])
        # actions[0] = np.array([1., 0.5])

        # Internal agents (running a pre-learned policy defined in envs/policies)
        # will automatically query their policy during env.step
        # ==> no need to supply actions for internal agents here

        # Run a simulation step (check for collisions, move sim agents)
        obs, rewards, game_over, which_agents_done = env.step(actions)

        print("observation",np.array(obs).shape)
        print("rewards",rewards)


        if game_over:
            print("All agents finished!")
            break
    env.reset()

    return True

if __name__ == '__main__':
    main()
    print("Experiment over.")