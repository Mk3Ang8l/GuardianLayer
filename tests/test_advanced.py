from LoopDetector import LoopDetector

def test_immediate_repeat():
    detector = LoopDetector()
    call = {"tool": "search", "query": "test"}
    
    # First call OK 
    assert detector.check(call) == (False, None)
    
    # Second call = loop
    is_loop, reason = detector.check(call)
    assert is_loop == True
    assert reason == "IMMEDIATE_REPEAT"

def test_different_calls():
    detector = LoopDetector()
    call1 = {"tool": "search", "query": "A"}
    call2 = {"tool": "search", "query": "B"}
    
    # Two differents calls = OK
    assert detector.check(call1) == (False, None)
    assert detector.check(call2) == (False, None)

def test_cycle_detection():
    detector = LoopDetector()
    call_a = {"tool": "search", "query": "A"}
    call_b = {"tool": "scrape", "url": "B"}
    
    detector.check(call_a)  # A
    detector.check(call_b)  # B
    detector.check(call_a)  # A (cycle A→B→A)
    
    is_loop, reason = detector.check(call_b)
    assert is_loop == True
    assert "CYCLE" in reason