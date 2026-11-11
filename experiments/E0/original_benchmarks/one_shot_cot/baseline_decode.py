"""Thin prompting-baseline decode path extracted from LLM4DBdesign/agent_format.py.

Supports only the Table VI prompting baselines:
  - base_direct + few_shot=False  → one-shot
  - base_direct + few_shot=True   → few-shot
  - base_cot    + few_shot=False  → one-shot+CoT

The SchemaAgent multi-agent implementation is intentionally excluded from this
release (it was not successfully reproduced for the ICDE artifact).

Provenance:
  - Original: /data/LLM4DBdesign/agent_format.py::fully_decode (base_direct / base_cot branches)
  - Prompts:  prompt_generator_format.py
"""

from __future__ import annotations

from prompt_generator_format import (
    get_cot_prompt,
    get_direct_few_shot_prompt,
    get_direct_prompt,
)


def fully_decode(question, handler, args):
    """Run one prompting baseline decode step.

    Returns a dict with keys ``question`` and ``answer`` (parsed JSON schema or
    raw payload from the handler). Temperature/max_tokens match the historical
    LLM4DBdesign PaperMethods local runs (temperature=0, max_tokens=4096).
    """
    method = getattr(args, "method", None)
    few_shot = bool(getattr(args, "few_shot", False))

    if method == "base_direct":
        prompt = get_direct_few_shot_prompt(question) if few_shot else get_direct_prompt(question)
        output, output_json = handler.get_output_multiagent(
            user_input=prompt,
            temperature=0,
            max_tokens=4096,
            system_role="",
        )
        return {"question": question, "answer": output_json, "raw_output": output}

    if method == "base_cot":
        # Table VI uses one-shot+CoT only (few_shot=False). few-shot+CoT exists in
        # the upstream library but is not a Table VI row.
        if few_shot:
            raise ValueError(
                "few-shot+CoT is not part of published Table VI; "
                "use method=base_cot with few_shot=False for One-shot+CoT."
            )
        prompt = get_cot_prompt(question)
        output, output_json = handler.get_output_multiagent(
            user_input=prompt,
            temperature=0,
            max_tokens=4096,
            system_role="",
        )
        return {"question": question, "answer": output_json, "raw_output": output}

    raise ValueError(
        f"Unsupported method for published baselines: {method!r}. "
        "SchemaAgent multi-agent path is intentionally excluded from this release."
    )
