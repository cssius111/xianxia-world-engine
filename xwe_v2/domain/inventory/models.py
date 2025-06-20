"""
XWE V2 Inventory System

Domain models for inventory and item management.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Item:
    """Base item class."""

    id: str
    name: str
    description: str = ""
    stack_size: int = 1
    max_stack: int = 99
    value: int = 0
    rarity: str = "common"  # common, uncommon, rare, epic, legendary
    item_type: str = "misc"  # misc, consumable, equipment, material

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "stack_size": self.stack_size,
            "max_stack": self.max_stack,
            "value": self.value,
            "rarity": self.rarity,
            "item_type": self.item_type,
        }


@dataclass
class InventorySlot:
    """A single inventory slot."""

    item: Optional[Item] = None
    quantity: int = 0

    @property
    def is_empty(self) -> bool:
        """Check if slot is empty."""
        return self.item is None or self.quantity <= 0

    def can_add(self, item: Item, quantity: int = 1) -> bool:
        """Check if can add items to this slot."""
        if self.is_empty:
            return True
        if self.item.id != item.id:
            return False
        return self.quantity + quantity <= self.item.max_stack

    def add(self, item: Item, quantity: int = 1) -> int:
        """
        Add items to slot.
        Returns the number of items that couldn't be added.
        """
        if self.is_empty:
            self.item = item
            self.quantity = 0

        if self.item.id != item.id:
            return quantity

        space_left = self.item.max_stack - self.quantity
        to_add = min(quantity, space_left)
        self.quantity += to_add

        return quantity - to_add

    def remove(self, quantity: int = 1) -> int:
        """
        Remove items from slot.
        Returns the number of items actually removed.
        """
        if self.is_empty:
            return 0

        to_remove = min(quantity, self.quantity)
        self.quantity -= to_remove

        if self.quantity <= 0:
            self.item = None
            self.quantity = 0

        return to_remove


class Inventory:
    """Character inventory system."""

    def __init__(self, capacity: int = 50):
        self.capacity = capacity
        self.slots: List[InventorySlot] = [InventorySlot() for _ in range(capacity)]
        self._item_index: Dict[str, List[int]] = {}  # item_id -> slot indices

    def add_item(self, item: Item, quantity: int = 1) -> int:
        """
        Add items to inventory.
        Returns the number of items that couldn't be added.
        """
        remaining = quantity

        # First, try to stack with existing items
        if item.id in self._item_index:
            for slot_idx in self._item_index[item.id]:
                slot = self.slots[slot_idx]
                remaining = slot.add(item, remaining)
                if remaining == 0:
                    return 0

        # Then, find empty slots
        for i, slot in enumerate(self.slots):
            if slot.is_empty:
                remaining = slot.add(item, remaining)
                if item.id not in self._item_index:
                    self._item_index[item.id] = []
                self._item_index[item.id].append(i)
                if remaining == 0:
                    return 0

        return remaining

    def remove_item(self, item_id: str, quantity: int = 1) -> int:
        """
        Remove items from inventory.
        Returns the number of items actually removed.
        """
        if item_id not in self._item_index:
            return 0

        total_removed = 0
        slots_to_check = self._item_index[item_id].copy()

        for slot_idx in slots_to_check:
            slot = self.slots[slot_idx]
            removed = slot.remove(quantity - total_removed)
            total_removed += removed

            if slot.is_empty:
                self._item_index[item_id].remove(slot_idx)

            if total_removed >= quantity:
                break

        if not self._item_index[item_id]:
            del self._item_index[item_id]

        return total_removed

    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """Check if inventory has enough of an item."""
        return self.count_item(item_id) >= quantity

    def count_item(self, item_id: str) -> int:
        """Count total quantity of an item."""
        if item_id not in self._item_index:
            return 0

        total = 0
        for slot_idx in self._item_index[item_id]:
            total += self.slots[slot_idx].quantity

        return total

    def get_items(self) -> List[Tuple[Item, int]]:
        """Get all items in inventory as (item, quantity) tuples."""
        items = []
        for slot in self.slots:
            if not slot.is_empty:
                items.append((slot.item, slot.quantity))
        return items

    def get_empty_slots(self) -> int:
        """Get number of empty slots."""
        return sum(1 for slot in self.slots if slot.is_empty)

    def clear(self) -> None:
        """Clear all items from inventory."""
        self.slots = [InventorySlot() for _ in range(self.capacity)]
        self._item_index.clear()

    def to_dict(self) -> Dict:
        """Convert inventory to dictionary."""
        items = []
        for slot in self.slots:
            if not slot.is_empty:
                items.append({"item": slot.item.to_dict(), "quantity": slot.quantity})

        return {"capacity": self.capacity, "items": items}

    @classmethod
    def from_dict(cls, data: Dict) -> "Inventory":
        """Create inventory from dictionary."""
        inventory = cls(capacity=data.get("capacity", 50))

        for item_data in data.get("items", []):
            item = Item(**item_data["item"])
            quantity = item_data["quantity"]
            inventory.add_item(item, quantity)

        return inventory
