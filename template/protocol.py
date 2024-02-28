# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# TODO(developer): Set your name
# Copyright © 2023 Juan Monrroy Reyes

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import random
import hashlib
import typing
import bittensor as bt

# TODO(developer): Rewrite with your protocol definition.

# This is the protocol for the dummy miner and validator.
# It is a simple request-response protocol where the validator sends a request
# to the miner, and the miner responds with a dummy response.

# ---- miner ----
# Example usage:
#   def dummy( synapse: Dummy ) -> Dummy:
#       synapse.dummy_output = synapse.dummy_input + 1
#       return synapse
#   axon = bt.axon().attach( dummy ).serve(netuid=...).start()

# ---- validator ---
# Example usage:
#   dendrite = bt.dendrite()
#   dummy_output = dendrite.query( Dummy( dummy_input = 1 ) )
#   assert dummy_output == 2

class Dummy(bt.Synapse):
    """
    A simple dummy protocol representation which uses bt.Synapse as its base.
    This protocol helps in handling dummy request and response communication between
    the miner and the validator.

    Attributes:
    - initial_nonce: Initial value for nonce. We used an incrementally focus.
    - min_difficulty: Min value for randomly simulate difficult.
    - max_difficulty: Man value for randomly simulate difficult.
    - nonce: Nonce value provided by the miner.
    - hash_result: Hash result produced by the miner using the provided nonce.
    - prev_hash: Previously hash produced.
    - transactions: Transactions included in the block.
    - base_reward: Base TAO quantity to reward
    """

    min_difficulty: int = 1
    max_difficulty: int = 4
    difficulty: int = random.randint(min_difficulty, max_difficulty)
    nonce: int = 0
    hash_result: str = None
    prev_hash: str = None
    base_reward: int = 100
    transactions: str = ''
    initial_nonce: int = 1

    # Required request input, filled by sending dendrite caller.
    def mine_hash(self) -> str:
        to_find_hash = str(self.initial_nonce+self.prev_hash+self.transactions)
        while True:
            hash_result = hashlib.sha256(to_find_hash.encode()).hexdigest()
            if hash_result.startswith('0' * self.difficulty):
                return hash_result
            self.initial_nonce += 1
            to_find_hash = str(self.initial_nonce+self.prev_hash+self.transactions)

    def validate_hash(self, hash_result: str,) -> bool:
        """
        Args:
        - hash_result: The hash produced by the miner.

        Returns:
        - bool: Hash fulfill with the difficulty (True / False)
        """
        if hash_result.startswith('0' * self.difficulty):
            self.prev_hash = hash_result
            return True
        return False

        