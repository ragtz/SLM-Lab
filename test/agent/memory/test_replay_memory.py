from collections import Counter
from copy import deepcopy
from flaky import flaky
import numpy as np
import pytest


@flaky
class TestMemory:
    '''
    Base class for unit testing replay memory
    Note: each test examples from test_memory consists of
          a tuple containing three elements:
          (memory, batch_size, experiences)
    '''

    def test_memory_init(self, test_memory):
        memory = test_memory[0]
        assert memory.true_size == 0
        assert memory.states.shape == (memory.max_size, memory.body.state_dim)
        assert memory.actions.shape == (memory.max_size,)
        assert memory.rewards.shape == (memory.max_size,)
        assert memory.dones.shape == (memory.max_size,)

    def test_add_experience(self, test_memory):
        '''Adds an experience to the memory. Checks that memory size = 1, and checks that the experience values are equal to the experience added'''
        memory = test_memory[0]
        memory.reset()
        experiences = test_memory[2]
        exp = experiences[0]
        memory.add_experience(*exp)
        assert memory.true_size == 1
        assert memory.head == 0
        # Handle states and actions with multiple dimensions
        assert np.array_equal(memory.states[memory.head], exp[0])
        assert memory.actions[memory.head] == exp[1]
        assert memory.rewards[memory.head] == exp[2]
        assert memory.dones[memory.head] == exp[4]

    def test_wrap(self, test_memory):
        '''Tests that the memory wraps round when it is at capacity'''
        memory = test_memory[0]
        memory.reset()
        experiences = test_memory[2]
        num_added = 0
        for e in experiences:
            memory.add_experience(*e)
            num_added += 1
            assert memory.true_size == min(memory.max_size, num_added)
            assert memory.head == (num_added - 1) % memory.max_size

    def test_sample(self, test_memory):
        '''Tests that a sample of batch size is returned with the correct dimensions'''
        memory = test_memory[0]
        memory.reset()
        batch_size = test_memory[1]
        experiences = test_memory[2]
        for e in experiences:
            memory.add_experience(*e)
        memory.batch_size = batch_size
        batch = memory.sample()
        assert batch['states'].shape == (batch_size, memory.body.state_dim)
        assert batch['actions'].shape == (batch_size,)
        assert batch['rewards'].shape == (batch_size,)
        assert batch['next_states'].shape == (batch_size, memory.body.state_dim)
        assert batch['dones'].shape == (batch_size,)

    @flaky(max_runs=10)
    def test_sample_changes(self, test_memory):
        '''Tests if memory.current_batch_indices changes from sample to sample'''
        memory = test_memory[0]
        memory.reset()
        batch_size = test_memory[1]
        experiences = test_memory[2]
        for e in experiences:
            memory.add_experience(*e)
        memory.batch_size = batch_size
        _batch = memory.sample()
        old_idx = deepcopy(memory.batch_idxs).tolist()
        for i in range(5):
            _batch = memory.sample()
            new_idx = memory.batch_idxs.tolist()
            assert old_idx != new_idx
            old_idx = deepcopy(memory.batch_idxs).tolist()

    def test_sample_next_states(self, test_memory):
        memory = test_memory[0]
        idxs = np.array(range(memory.true_size))
        next_states = memory._sample_next_states(idxs)
        assert np.array_equal(next_states[len(next_states) - 1], memory.latest_next_state)

    def test_reset(self, test_memory):
        '''Tests memory reset. Adds 2 experiences, then resets the memory and checks if all appropriate values have been zeroed'''
        memory = test_memory[0]
        memory.reset()
        experiences = test_memory[2]
        for i in range(2):
            e = experiences[i]
            memory.add_experience(*e)
        memory.reset()
        assert memory.head == -1
        assert memory.true_size == 0
        assert np.sum(memory.states) == 0
        assert np.sum(memory.actions) == 0
        assert np.sum(memory.rewards) == 0
        assert np.sum(memory.dones) == 0

    @pytest.mark.skip(reason="Not implemented yet")
    def test_sample_dist(self, test_memory):
        '''Samples 100 times from memory. Accumulates the indices sampled and checks for significant deviation from a uniform distribution'''
        # TODO test_sample_dist
        assert None is None
