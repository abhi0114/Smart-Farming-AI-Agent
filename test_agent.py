"""
Quick smoke-test for the Smart Farming AI Agent.
Run with: python test_agent.py
Does NOT require IBM credentials — uses mock responses.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))


async def test_agent():
    print("=" * 60)
    print("  Smart Farming AI Agent — Smoke Test")
    print("  IBM Granite + RAG Pipeline")
    print("=" * 60)

    from app.agents.farming_agent import farming_agent, AgentRequest

    test_cases = [
        AgentRequest(query="What crop should I plant this June?",           location="Pune"),
        AgentRequest(query="What is today's mandi rate for tomatoes?",      crop="Tomato"),
        AgentRequest(query="How do I control pests in my wheat field?"),
        AgentRequest(query="What fertilizer should I use for paddy?"),
        AgentRequest(query="टमाटर का आज का मंडी भाव क्या है?",             language="hi"),
        AgentRequest(query="माझ्या शेतासाठी कोणते पीक योग्य आहे?",         language="mr"),
    ]

    for i, req in enumerate(test_cases, 1):
        print(f"\n[Test {i}] Query: {req.query[:60]}...")
        print(f"         Location: {req.location} | Language: {req.language} | Crop: {req.crop}")
        try:
            response = await farming_agent.run(req)
            print(f"  ✅ Intent:    {response.intent}")
            print(f"  ✅ Language:  {response.detected_language}")
            print(f"  ✅ Answer:    {response.answer[:150]}...")
            if response.sources:
                print(f"  ✅ Sources:   {', '.join(response.sources[:3])}")
        except Exception as exc:
            print(f"  ❌ ERROR: {exc}")

    print("\n" + "=" * 60)
    print("  Smoke test complete!")
    print("=" * 60)


async def test_rag():
    print("\n--- RAG Engine Test ---")
    from app.rag.engine import rag_engine
    rag_engine.initialize()
    print(f"  Chunks loaded: {len(rag_engine._chunks)}")
    results = rag_engine.retrieve("pest control for paddy", top_k=3)
    print(f"  Retrieved {len(results)} chunks for 'pest control for paddy'")
    for r in results:
        print(f"    [{r.category}] {r.source}: {r.text[:80]}...")


async def test_market():
    print("\n--- Market Service Test ---")
    from app.services.market import market_service
    prices = await market_service.get_prices()
    print(f"  Prices available for {len([k for k in prices if k not in ('timestamp', '_note')])} crops")
    if "Tomato" in prices:
        print(f"  Tomato modal price: ₹{prices['Tomato']['modal']}/quintal")


async def test_weather():
    print("\n--- Weather Service Test ---")
    from app.services.weather import weather_service
    weather = await weather_service.get_weather("Pune")
    print(f"  Location: {weather['location']}, Temp: {weather['temp']}°C, Humidity: {weather['humidity']}%")


if __name__ == "__main__":
    async def main():
        await test_rag()
        await test_weather()
        await test_market()
        await test_agent()

    asyncio.run(main())
