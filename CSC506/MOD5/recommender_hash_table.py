# recommender_hash_table.py
# Author: Justan E. Dunn
# Date: 2025-10-13
# Purpose: Hash-table-based content recommendation prototype with real-time updates.

from collections import defaultdict, deque
from time import time

class HashRecommender:
    """
    Core structures (all hash-table based):
      - user_interests: user_id -> set(tags)
      - tag_buckets: tag -> deque of (content_id, score_ts)
      - content_meta: content_id -> { 'tags': set, 'score_ts': float }
    Uses chaining internally via Python dict + dynamic resizing.
    """

    def __init__(self, bucket_cap=10):
        self.user_interests = defaultdict(set)
        self.tag_buckets = defaultdict(lambda: deque(maxlen=bucket_cap))
        self.content_meta = {}
        self.bucket_cap = bucket_cap

    def add_user_interest(self, user_id, tag):
        # avg O(1)
        self.user_interests[user_id].add(tag)

    def remove_user_interest(self, user_id, tag):
        self.user_interests[user_id].discard(tag)

    def add_content(self, content_id, tags, score_ts=None):
        """
        Add content once; push to each tag bucket. Dedup by content_id.
        score_ts can combine recency + relevance; here we use timestamp.
        """
        if score_ts is None:
            score_ts = time()
        self.content_meta[content_id] = {"tags": set(tags), "score_ts": score_ts}

        for t in tags:
            # Avoid duplicates in a bucket (O(k) with tiny k due to capped deque)
            bucket = self.tag_buckets[t]
            if not any(cid == content_id for cid, _ in bucket):
                bucket.appendleft((content_id, score_ts))  # newest first

    def update_content_score(self, content_id, new_score_ts=None):
        if content_id not in self.content_meta:
            return
        if new_score_ts is None:
            new_score_ts = time()
        # Update meta
        self.content_meta[content_id]["score_ts"] = new_score_ts
        # Re-insert at front of each tag bucket (simple recency bump)
        for t in self.content_meta[content_id]["tags"]:
            bucket = self.tag_buckets[t]
            # remove existing entry
            for i, (cid, _) in enumerate(bucket):
                if cid == content_id:
                    del bucket[i]
                    break
            bucket.appendleft((content_id, new_score_ts))

    def recommend(self, user_id, k=10):
        """
        Merge candidate lists from all user tags, deduplicate via hash set,
        and return top-k by score_ts (newest first).
        Complexity: O(C) where C is total candidates scanned across user tags.
        """
        tags = self.user_interests.get(user_id, set())
        seen = set()
        candidates = []

        # Gather recent items per tag (O(1) per append; small bounded buckets)
        for t in tags:
            for cid, score in self.tag_buckets.get(t, []):
                if cid not in seen:
                    seen.add(cid)
                    candidates.append((cid, score))

        # Sort by score_ts descending (tiny working set due to bucket caps)
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [cid for cid, _ in candidates[:k]]

    # --- Debug / Display helpers for screenshots ---
    def print_state(self):
        print("Users -> Interests")
        for u, tags in self.user_interests.items():
            print(f"  {u}: {sorted(tags)}")
        print("\nTag Buckets (most recent first)")
        for t, bucket in self.tag_buckets.items():
            ids = [cid for cid, _ in bucket]
            print(f"  {t}: {ids}")

    def print_recs(self, user_id, k=10):
        print(f"\nRecommendations for {user_id} (top {k}): {self.recommend(user_id, k)}")


if __name__ == "__main__":
    rec = HashRecommender(bucket_cap=8)

    # === Figure 1: Initial state ===
    # Users & interests
    rec.add_user_interest("alice", "music.pop")
    rec.add_user_interest("alice", "fitness")
    rec.add_user_interest("bob", "tech.ai")
    rec.add_user_interest("bob", "gaming.rpg")

    # Seed content
    rec.add_content("c101", ["music.pop"], score_ts=time()-50)
    rec.add_content("c102", ["music.pop", "fitness"], score_ts=time()-40)
    rec.add_content("c201", ["tech.ai"], score_ts=time()-30)
    rec.add_content("c202", ["gaming.rpg"], score_ts=time()-20)
    rec.add_content("c203", ["gaming.rpg", "tech.ai"], score_ts=time()-10)

    print("=== FIGURE 1: Initial Users/Tags and Tag Buckets ===")
    rec.print_state()

    # === Figure 2: Real-time updates ===
    rec.add_user_interest("alice", "tech.ai")           # user behavior update
    rec.add_content("c301", ["fitness"], score_ts=time())  # new content arrives
    rec.update_content_score("c201", time())            # engagement bump on c201

    print("\n=== FIGURE 2: After Updates (new interest + new content + score bump) ===")
    rec.print_state()

    # === Figure 3: Recommendations ===
    print("\n=== FIGURE 3: Recommendations ===")
    rec.print_recs("alice", k=5)
    rec.print_recs("bob", k=5)
