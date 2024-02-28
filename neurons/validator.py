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
import time

# Bittensor
import bittensor as bt

# Bittensor Validator Template:
import template
from template.validator import forward

# import base validator class which takes care of most of the boilerplate
from template.base.validator import BaseValidatorNeuron

wallet: "bt.wallet"

class Validator(BaseValidatorNeuron):
    """
    Your validator neuron class. You should use this class to define your validator's behavior. In particular, you should replace the forward function with your own logic.

    This class inherits from the BaseValidatorNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a validator such as keeping a moving average of the scores of the miners and using them to set weights at the end of each epoch. Additionally, the scores are reset for new hotkeys at the end of each epoch.
    """

    def __init__(self, config=None):
        super(Validator, self).__init__(config=config)

        bt.logging.info("load_state()")
        self.load_state()
        self.miner_performance = {}
        self.performace_range = {
            (float('-inf'), 0): 0,
            (0, 100): 0.1,
            (100, 1000): 0.2,
            (1000, 5000): 0.3,
            (5000, 10000): 0.4,
            (10000, float('inf')): 0.5
        }

        self.dummy_instance = template.protocol.Dummy()  


        # TODO(developer): Anything specific to your use case you can do here

    def data_to_hash(self):
        bt.logging.info("Exec data_to_hash")
        block_timestamp = int(time.time())
        tx_block_count = random.randint(1, 10)
        tx_list = [str(block_timestamp)]
        for i in range(1, tx_block_count + 1):
            tx_list.append("tx" + str(i))
        data = "-".join(tx_list)
        return data

    async def querying_miners(self, block_transactions: str):
        bt.logging.info("Exec querying_miners")
        miner_responses = {}
        synapse = template.protocol.Dummy(transactions=block_transactions)
        for hotkey in validator.metagraph.hotkeys:
            response = validator.dendrite.query(synapse, hotkey=hotkey)
            if response is not None:
                response = await response
                miner_responses[hotkey] = response
        return miner_responses

    async def check_responses(self, responses):
        bt.logging.info("Exec check_responses")
        for hotkey, response in responses.items():
            if await self.validate_hash(response.hash_result):
                if hotkey in self.miner_performance:
                    self.miner_performance[hotkey] += 1
                else:
                    self.miner_performance[hotkey] = 1
                return hotkey
        return None

    def calculate_reward(self, hotkey):
        bt.logging.info("Exec calculate_reward")
        base_reward = self.dummy_instance.base_reward
        if hotkey not in self.miner_performance:
            return base_reward 
        miner_performance = self.miner_performance[hotkey]
        performance_factor = next(valor for rangos, valor in self.performace_range.items() if rangos[0] <= miner_performance < rangos[1])
        aditional_reward = base_reward * performance_factor
        final_reward = base_reward + aditional_reward
        return final_reward

    async def forward(self):
        """
        Validator forward pass. Consists of:
        - Generating the query
        - Querying the miners
        - Getting the responses
        - Rewarding the miners
        - Updating the scores
        """
        # TODO(developer): Rewrite this function based on your protocol definition.

        subtensor = bt.subtensor()


        block_transactions = self.data_to_hash()
        #Send to miners
        responses = await self.querying_miners(block_transactions)
        #Check de responses
        uid_minner_winer = self.check_responses(responses)
        #Calculate ward and send tokens
        if uid_minner_winer is not None:
            reward = self.calculate_reward(uid_minner_winer)
            subtensor.get_current_block()
            #await self.transfer(uid_minner_winer, reward)
            bt.logging.info("TAO Rewarding: ", str(reward))
            bt.logging.info("To id miner: ", uid_minner_winer)
        return await forward(self)


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    with Validator() as validator:
        while True:
            bt.logging.info("Validator running...", time.time())
            time.sleep(5)
