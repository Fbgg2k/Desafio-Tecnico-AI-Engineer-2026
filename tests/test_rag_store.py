from src.agent.tools import rag_tool


def test_retrieve_policy_returns_relevant_chunk():
    results = rag_tool.retrieve_policy("troca e devoluções", top_k=2)
    assert len(results) >= 1
    top = results[0]
    assert "content" in top
    assert "score" in top
