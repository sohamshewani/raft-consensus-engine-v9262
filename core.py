from typing import List, Dict, Optional, Tuple
import threading
import time
import random

class Node:
    def __init__(self, id: int, peers: List[int]):
        self.id = id
        self.peers = peers
        self.state = 'follower'
        self.voted_for = None
        self.current_term = 0
        self.log = []
        self.commit_index = 0
        self.last_applied = 0
        self.next_index = {peer: len(self.log) for peer in peers}
        self.match_index = {peer: 0 for peer in peers}
        self.lock = threading.Lock()

    def become_follower(self):
        with self.lock:
            self.state = 'follower'
            self.voted_for = None
            self.current_term += 1

    def become_candidate(self):
        with self.lock:
            self.state = 'candidate'
            self.current_term += 1
            self.voted_for = self.id
            self.send_votes()

    def become_leader(self):
        with self.lock:
            self.state = 'leader'
            for peer in self.peers:
                self.next_index[peer] = len(self.log)
                self.match_index[peer] = 0

    def send_votes(self):
        for peer in self.peers:
            threading.Thread(target=self.request_vote, args=(peer,)).start()

    def request_vote(self, peer: int):
        with self.lock:
            if self.state != 'candidate':
                return

        # Simulate network delay
        time.sleep(random.uniform(0.1, 0.5))

        with self.lock:
            if self.state != 'candidate':
                return

            if self.current_term > self.log[0]['term']:
                return

            if self.voted_for is None or self.voted_for == self.id:
                self.voted_for = self.id
                self.send_append_entries(peer)

    def send_append_entries(self, peer: int):
        with self.lock:
            if self.state != 'leader':
                return

        # Simulate network delay
        time.sleep(random.uniform(0.1, 0.5))

        with self.lock:
            if self.state != 'leader':
                return

            prev_log_index = self.next_index[peer] - 1
            prev_log_term = self.log[prev_log_index]['term'] if prev_log_index >= 0 else None

            entry = self.log[self.next_index[peer]:]

            args = {
                'term': self.current_term,
                'prev_log_index': prev_log_index,
                'prev_log_term': prev_log_term,
                'entries': entry,
                'leader_commit': self.commit_index
            }

            threading.Thread(target=self.append_entries, args=(peer, args)).start()

    def append_entries(self, peer: int, args: Dict):
        with self.lock:
            if self.state != 'leader':
                return

        # Simulate network delay
        time.sleep(random.uniform(0.1, 0.5))

        with self.lock:
            if self.state != 'leader':
                return

            if args['term'] < self.current_term:
                return

            if args['term'] > self.current_term:
                self.current_term = args['term']
                self.become_follower()

            if args['prev_log_index'] >= len(self.log) or (args['prev_log_index'] >= 0 and self.log[args['prev_log_index']]['term'] != args['prev_log_term']):
                return

            self.log = self.log[:args['prev_log_index'] + 1] + args['entries']
            self.match_index[peer] = args['prev_log_index'] + len(args['entries'])
            self.next_index[peer] = self.match_index[peer] + 1

            self.apply_logs()

    def apply_logs(self):
        with self.lock:
            for i in range(self.last_applied + 1, self.commit_index + 1):
                entry = self.log[i]
                # Apply the log entry to the state machine
                print(f"Node {self.id} applied log entry: {entry}")
                self.last_applied = i

    def run(self):
        while True:
            if self.state == 'follower':
                time.sleep(random.uniform(0.1, 0.5))
            elif self.state == 'candidate':
                time.sleep(random.uniform(0.1, 0.5))
            elif self.state == 'leader':
                time.sleep(random.uniform(0.1, 0.5))

            with self.lock:
                if self.state == 'follower':
                    self.become_candidate()
                elif self.state == 'candidate':
                    self.send_votes()
                elif self.state == 'leader':
                    self.send_append_entries()

# Example usage
nodes = [Node(id, [1, 2, 3]) for id in range(1, 4)]
for node in nodes:
    threading.Thread(target=node.run).start()