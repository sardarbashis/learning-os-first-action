import json
from pathlib import Path
from datetime import datetime

import streamlit as st


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="Learning OS",
    page_icon="🧠",
    layout="centered",
)

DATA_DIR = Path(__file__).parent
CONTEXT_FILE = DATA_DIR / "learner_context.json"
HISTORY_FILE = DATA_DIR / "session_history.json"


# ---------------------------------------------------------
# Storage helpers
# ---------------------------------------------------------

def load_json(path: Path, default):
    if not path.exists():
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_context():
    return load_json(CONTEXT_FILE, {
        "goal": "",
        "current_level": "",
        "known": "",
        "learning_now": "",
        "struggling_with": "",
        "current_project": "",
        "learning_preferences": "",
        "last_session_summary": "",
        "next_step": "",
        "updated_at": "",
    })


def load_history():
    return load_json(HISTORY_FILE, [])


# ---------------------------------------------------------
# Learning continuation logic
# ---------------------------------------------------------

def build_next_step(context):
    goal = context.get("goal", "").strip()
    learning_now = context.get("learning_now", "").strip()
    struggling = context.get("struggling_with", "").strip()
    next_step = context.get("next_step", "").strip()

    if next_step:
        return next_step

    if struggling:
        return (
            f"Work on the current difficulty: {struggling}. "
            f"Use one focused resource, then explain the concept back in your own words."
        )

    if learning_now:
        return (
            f"Continue with the current topic: {learning_now}. "
            f"Do one small practical exercise before moving to another topic."
        )

    if goal:
        return (
            f"Choose one small learning task that moves you toward: {goal}. "
            f"Complete that task before adding another resource."
        )

    return "Define one specific learning goal and one small task for today's session."


# ---------------------------------------------------------
# UI
# ---------------------------------------------------------

context = load_context()
history = load_history()

st.title("🧠 Learning OS")
st.caption("Persistent learning context — continue from where you left off.")

st.divider()

# ---------------------------------------------------------
# Section 1: Learner context
# ---------------------------------------------------------

st.header("Your Learning Context")

goal = st.text_input(
    "Learning goal",
    value=context.get("goal", ""),
    placeholder="Example: Become an FDE",
)

current_level = st.text_input(
    "Current level",
    value=context.get("current_level", ""),
    placeholder="Example: Beginner",
)

known = st.text_area(
    "What do you already know?",
    value=context.get("known", ""),
    placeholder="Example: Python, APIs, basic AI",
)

learning_now = st.text_input(
    "What are you learning right now?",
    value=context.get("learning_now", ""),
    placeholder="Example: AI agents",
)

struggling_with = st.text_area(
    "What are you struggling with?",
    value=context.get("struggling_with", ""),
    placeholder="Example: Tool calling and agent memory",
)

current_project = st.text_input(
    "Current project",
    value=context.get("current_project", ""),
    placeholder="Example: Building an AI agent",
)

learning_preferences = st.text_input(
    "How do you prefer to learn?",
    value=context.get("learning_preferences", ""),
    placeholder="Example: Video + practical exercises",
)

st.subheader("Current Session")

session_summary = st.text_area(
    "What did you learn / do in this session?",
    placeholder="Example: I learned how tool calling works and built a small example.",
)

next_step_input = st.text_area(
    "What should you continue with next?",
    value=context.get("next_step", ""),
    placeholder="Example: Build a tool-calling example without copying the tutorial.",
)


# ---------------------------------------------------------
# Save button
# ---------------------------------------------------------

if st.button("💾 Save Learning Context", use_container_width=True):

    now = datetime.now().isoformat(timespec="seconds")

    updated_context = {
        "goal": goal,
        "current_level": current_level,
        "known": known,
        "learning_now": learning_now,
        "struggling_with": struggling_with,
        "current_project": current_project,
        "learning_preferences": learning_preferences,
        "last_session_summary": session_summary,
        "next_step": next_step_input,
        "updated_at": now,
    }

    # Save the new context to disk
    save_json(CONTEXT_FILE, updated_context)

    # IMPORTANT:
    # Update the in-memory context too, so the sections
    # below immediately use the newly saved values.
    context = updated_context

    if session_summary.strip():
        history.append({
            "timestamp": now,
            "summary": session_summary,
            "next_step": next_step_input,
        })

        save_json(HISTORY_FILE, history)

    st.success("Learning context saved.")


# ---------------------------------------------------------
# Continue learning
# ---------------------------------------------------------

st.divider()

st.header("Continue Learning")

if context.get("updated_at"):
    st.info(
        f"Last saved: {context['updated_at']}"
    )

continuation = build_next_step(context)

st.markdown("### Where you should continue")
st.write(continuation)

if context.get("last_session_summary"):
    st.markdown("### Last session")
    st.write(context["last_session_summary"])

if context.get("goal"):
    st.markdown("### Goal")
    st.write(context["goal"])

if context.get("struggling_with"):
    st.markdown("### Current difficulty")
    st.write(context["struggling_with"])

# ---------------------------------------------------------
# History
# ---------------------------------------------------------

if history:
    st.divider()
    st.header("Learning History")

    for item in reversed(history[-5:]):
        with st.container(border=True):
            st.write(f"**{item['timestamp']}**")
            st.write(item["summary"])

            if item.get("next_step"):
                st.caption(f"Next: {item['next_step']}")