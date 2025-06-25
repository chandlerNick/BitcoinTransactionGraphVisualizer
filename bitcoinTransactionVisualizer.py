# Nicholas Chandler
# 30.01.2025
# Bitcoin blockchain transaction visualizer - rough version

import networkx as nx 
import requests
import matplotlib.pyplot as plt

class BlockchainGraph:
    """Class containing functionailty to assemble and visualize the blockchain graph
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()
    
    def add_transaction(self, tx):
        """Add transaction to the graph

        Args:
            tx (JSON): JSON including the sender and reciever addresses
        """
        for vin in tx['vin']:
            if vin.get('is_coinbase', False):
                sender_address = "Coinbase Transaction"
                reciever_address = tx['vout'][0].get('scriptpubkey', 'Unknown address')
            elif 'prevout' in vin and vin['prevout']:
                sender_address = vin['prevout'].get('scriptpubkey', 'Unknown address')
                reciever_address = tx['vout'][0].get('scriptpubkey', 'Unknown address')
            else:  # Not a valid transaction (i.e. no sender/reciever)
                continue
            #print("Sender addr: ", sender_address, "\nReciever addr: ", reciever_address)
            # Add nodes & edges to graph
            self.graph.add_node(sender_address)
            self.graph.add_node(reciever_address)
            self.graph.add_edge(sender_address, reciever_address)
    
    def visualize(self):
        """Visualize the current state of the graph.
        """
        shortened_labels = {node: node[:8] for node in self.graph.nodes}
        
        pos = nx.spring_layout(self.graph, k=0.5, iterations=50)
        
        nx.draw(self.graph, pos, with_labels=True, labels=shortened_labels, font_size=10)
        plt.show()
    
    def fetch_and_add_block(self, block_height):
        """Fetch a block by its height and add transactions to graph

        Args:
            block_height (str): nonnegative numerical value as string indicating height
        """
        block_data = Block.get_block_transactions(block_height)
        
        if block_data:
            try:
                for tx in block_data:
                    #print(tx)
                    self.add_transaction(tx)
            except Exception as e:
                print(f"(fetch_and_add_block): {e}")
        
class Block:
    """Class for the retrieving blocks
    """
    
    @staticmethod
    def get_block_hash(block_height):
        """Gets the block hash given the block height

        Args:
            block_height (str): nonnegative integer as string denoting block height

        Returns:
            str: hashcode for block to retrieve
        """
        url = f"https://blockstream.info/api/block-height/{block_height}"
        response = requests.get(url)
  
        # Check if the response is successful
        if response.status_code != 200:
            print(f"Error in get_block_hash: Recieved {response.status_code}")
            print("Response Content:", response.text)  # Print the raw response content
            return None

        return str(response.text)  # return the response text
    
    @staticmethod
    def get_block_data(block_height):
        """Fetch block data from the Blockstream API by block height.

        Args:
            block_height (str): nonnegative integer as string denoting the block height. 
        
        Returns:
            JSON: block json
        """
        block_hash = Block.get_block_hash(block_height)
        url = f"https://blockstream.info/api/block/{block_hash}"
        response = requests.get(url)
        
        # Check if the response is successful
        if response.status_code != 200:
            print(f"Error in get_block_data: Recieved {response.status_code}")
            print("Response Content:", response.text)  # Print the raw response content
            return None
        
        try:
            return response.json()
        except ValueError as e:
            print(f"Error decoding JSON in get_block_data: {e}")
            print("Response Content:", response.text)
            return None
    
    @staticmethod
    def get_block_transactions(block_height):
        """Fetches the transactions assoc'd with a block of specified height

        Args:
            block_height (str): nonnegative integer as string that denotes the block height

        Returns:
            json list: list of transaction json
        """
        block_hash = Block.get_block_hash(block_height)
        url = f'https://blockstream.info/api/block/{block_hash}/txs'
        response = requests.get(url)
        
        if response.status_code == 200:
            tx_data = response.json()
            return tx_data
        else:
            print(f"Error fetching transactions: {response.status_code}")
            return None
        

class Transaction:
    """Class for processing and storing transaction data
    """
    def __init__(self, tx_data):
        self.tx_data = tx_data
    
    def extract_addresses(self):
        """Extracts the sender and reciever addresses from a transaction
        """
        addresses = []
        for vin in self.tx_data['vin']:
            if 'prevout' in vin and vin['prevout']:
                addresses.append(vin['prevout']['scriptpubkey_address'])
        for vout in self.tx_data['vout']:
            addresses.append(vout['scriptpubkey_address'])
        return addresses

def main():
    blockchain_graph = BlockchainGraph()
    
    # Fetch a range of blocks and add blocks to the graph
    for block_height in range(881485,881487):  # CHANGE THIS RANGE FUNCTION TO SEE DIFFERENT GRAPHS!
        print(block_height)
        blockchain_graph.fetch_and_add_block(str(block_height))

    blockchain_graph.visualize()

if __name__ == "__main__":
    main()
