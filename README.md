# Hash Resolver

Foobar is a Python library for dealing with word pluralization.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install bittensor.

```bash
pip install bittensor
```

## Explanation
This repo is an initial version to a hash solver like works in Bitcoin.

We only explain the main features.
___
- template/protocol.py

We find the necessaries variables to resolve the hash and make the validation
```python
# In this demo, we set the random difficulty between 1 and 4
min_difficulty: int = 1
max_difficulty: int = 4
difficulty: int = random.randint(min_difficulty, max_difficulty)
# Set the initial necessaries values like nonce, previous hash and reward.
nonce: int = 0
hash_result: str = None
prev_hash: str = None
base_reward: int = 100
transactions: str = ''
initial_nonce: int = 1
```
Also defined mine_hash, to find the hash who use initial_nonce, previous hash, transactions

```python
def mine_hash(self) -> str:
    to_find_hash = str(self.initial_nonce+self.prev_hash+self.transactions)
    while True:
        hash_result = hashlib.sha256(to_find_hash.encode()).hexdigest()
        if hash_result.startswith('0' * self.difficulty):
            return hash_result
        self.initial_nonce += 1
        to_find_hash = str(self.initial_nonce+self.prev_hash+self.transactions)
```

And validate_hash to validate the result of mine_hash and if is correct, persist like previous hash.
```python
def validate_hash(self, hash_result: str,) -> bool:
    if hash_result.startswith('0' * self.difficulty):
        self.prev_hash = hash_result
        return True
    return False
```
___
- neurons/miner.py

We have a process_transaction_fee, who simulated a fee used to prioritize requests.
```python
async def process_transaction_fee(self, synapse: template.protocol.Dummy) -> None:
    transaction_fee = random.randint(0, 100)
    synapse.priority = transaction_fee
    bt.logging.info(f"Transaction fee: {transaction_fee}")
```
And, in forward function we call to mine_hash.
```python
hash_result = synapse.mine_hash()
synapse.hash_result = hash_result
```
___
- neurons/validator.py

  The forward calls to the next functions.

- **data_to_hash**: Simulate the transactions string incluing the block timestamp.

```python
def data_to_hash(self):
    bt.logging.info("Exec data_to_hash")
    block_timestamp = int(time.time())
    tx_block_count = random.randint(1, 10)
    tx_list = [str(block_timestamp)]
    for i in range(1, tx_block_count + 1):
        tx_list.append("tx" + str(i))
    data = "-".join(tx_list)
    return data
```

- **querying_miners**: Used to send de transactions to miners.

```python
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
```

- **data_to_hash**: Check the responses and add to the miner a counter (`miner_performance`) for each hash resolved.

```python
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
```

- **calculate_reward**: According to miner_performance and base reward, calculate the final reward

```python
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
```

The previous function use the next table to aditional fees for rango of hash resolved.
```python
self.performace_range = {
    (float('-inf'), 0): 0,
    (0, 100): 0.1,
    (100, 1000): 0.2,
    (1000, 5000): 0.3,
    (5000, 10000): 0.4,
    (10000, float('inf')): 0.5
}
```
___

## Important

This is not a final versión of the script, it still need some improvements

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)