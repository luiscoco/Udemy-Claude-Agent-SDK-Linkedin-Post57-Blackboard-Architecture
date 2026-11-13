"""Lesson-specific workflow. Read this file before the execution adapter."""
from __future__ import annotations
import asyncio
import json
from pathlib import Path
from runtime import atomic_json, contained_path, in_process_tool

def append_entry(board, expected_version, entry):
    if expected_version != board['version']:
        raise ValueError('Stale blackboard version; reread before updating')
    if any(item['id'] == entry['id'] for item in board['entries']):
        raise ValueError('Duplicate blackboard entry')
    board['entries'].append(entry)
    board['version'] += 1


async def run(agent, data):
    board = {'version': 0, 'entries': []}
    for index, evidence in enumerate(data['evidence']):
        append_entry(board, board['version'], {'id': 'E' + str(index + 1), 'author': 'collector', 'text': evidence})
    analysis = await agent.ask('analyst', 'Interpret the shared evidence without claiming an action was performed.', board, 'Investigate the two charges; a refund is not confirmed.')
    append_entry(board, board['version'], {'id': 'A1', 'author': 'analyst', 'text': analysis})
    atomic_json(agent.output / 'blackboard.json', board)
    return {'board': board, 'analysis': analysis}
