import os
import traceback
from dotenv import load_dotenv
from src.db import Database
from typing import Optional, List
from pydantic import BaseModel, Field
import streamlit as st

load_dotenv()


class CompetitorInsights(BaseModel):
    asin: str
    title: Optional[str]
    price: Optional[float]
    currency: Optional[str]
    rating: Optional[float]
    key_points: List[str] = Field(default_factory=list)


class AnalysisOutput(BaseModel):
    summary: str
    positioning: str
    top_competitors: List[CompetitorInsights]
    recommendations: List[str]


def format_competitors(db, parent_asin):
    comps = db.search_products({"parent_asin": parent_asin})
    return [
        {
            "asin": c["asin"],
            "title": c.get("title"),
            "price": c.get("price"),
            "currency": c.get("currency"),
            "rating": c.get("rating"),
            "amazon_domain": c.get("amazon_domain")
        }
        for c in comps
    ]


def analyze_competitors(asin):
    try:
        from langchain_openai import ChatOpenAI
        from langchain.prompts import PromptTemplate
        from langchain_core.output_parsers import PydanticOutputParser

        db = Database()
        # db.get_product returns a list — take first item if present
        product_record = db.get_product(asin)
        product = product_record[0] if product_record else None

        competitors = format_competitors(db, asin)

        parser = PydanticOutputParser(pydantic_object=AnalysisOutput)

        template = (
            "You are a market analyst. Given a product and its competitor list, "
            "write a concise analysis. Pay attention to currency and pricing context.\n\n"
            "Product Title: {product_title}\n"
            "Brand: {brand}\n"
            "Price: {currency} {price}\n"
            "Rating: {rating}\n"
            "Categories: {categories}\n"
            "Amazon Domain: {amazon_domain}\n\n"
            "Competitors (JSON): {competitors}\n\n"
            "IMPORTANT: All prices should be displayed with their correct currency symbol. "
            "When comparing prices, ensure you're using the same currency context.\n\n"
            "{format_instructions}"
        )

        prompt = PromptTemplate(
            template=template,
            input_variables=["product_title", "brand", "price", "rating", "categories", "amazon_domain", "competitors"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )

        # Model selection via environment
        model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

        # Basic API key presence check
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
        if not api_key:
            st.error("OpenAI API key not set. Please set OPENAI_API_KEY in your environment.")
            return "Error: OpenAI API key not set."

        llm = ChatOpenAI(model=model_name, temperature=0)

        chain = prompt | llm | parser

        try:
            result = chain.invoke(
                {
                    "product_title": product["title"] if product else asin,
                    "brand": product.get("brand") if product else None,
                    "price": product.get("price") if product else None,
                    "currency": product.get("currency") if product else "",
                    "rating": product.get("rating") if product else None,
                    "categories": product.get("categories") if product else None,
                    "amazon_domain": product.get("amazon_domain") if product else "com",
                    "competitors": competitors,
                }
            )
        except Exception as e:
            tb = traceback.format_exc()
            st.error(f"LLM error: {e}")
            st.text_area("Traceback (truncated)", tb[:8000], height=300)
            return f"Error running LLM: {e}"

        lines = [
            "Summary:\n" + result.summary,
            "\nPositioning:\n" + result.positioning,
            "\nCompetitors:"
        ]
        for c in result.top_competitors[:5]:
            pts = "; ".join(c.key_points) if c.key_points else ""
            currency = c.currency if c.currency else ""
            price_str = f"{currency} {c.price}" if currency else f"${c.price}"
            lines.append(f"- {c.asin} | {c.title} | {price_str} | {c.rating} | {pts}")

        if result.recommendations:
            lines.append("\nRecommendations:")
            for r in result.recommendations:
                lines.append(f"- {r}")

        return "\n".join(lines)
    except Exception as e:
        tb = traceback.format_exc()
        st.error("Unexpected error running LLM flow. Check OPENAI_API_KEY and OPENAI_MODEL environment variables.")
        st.text_area("Traceback (truncated)", tb[:8000], height=300)
        return f"Unexpected error: {e}"