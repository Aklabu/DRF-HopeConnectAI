from urllib.parse import quote_plus
import pandas as pd
 
MAX_CHARS = 3000
 
KEYWORDS = [
    "food", "medical", "resources", "shelter", "support", "abuse", "cooling",
    "education", "family", "housing", "hygiene", "meal", "pantry", "mental", "treatment"
]
 
SEMANTIC_MAP = {
    "hungry": ["food", "meal", "pantry"],
    "eat": ["food", "meal"],
    "doctor": ["medical", "treatment"],
    "clinic": ["medical"],
    "unsafe": ["shelter", "support", "abuse"],
    "violence": ["abuse", "support"],
    "shower": ["hygiene"],
    "bathroom": ["hygiene"],
    "school": ["education"],
    "kids": ["family", "education"],
    "home": ["housing", "shelter"],
    "mental": ["mental", "treatment", "support"],
    "cool": ["cooling"],
    "hot": ["cooling"],
    "harassment": ["abuse", "support"]
}
 
 
class file_uploder:
 
    def preprocess_csv(df):
        df_subset = df[['Provider', 'Category_New', 'Service_Type', 'Address']].copy()
        df_subset['Google_Maps_Link'] = df_subset['Address'].apply(
            lambda x: f"https://www.google.com/maps/search/?api=1&query={quote_plus(str(x))}" if pd.notna(x) else None
        )
        return df_subset
 
    def extract_keywords(text):
        return [kw for kw in KEYWORDS if kw.lower() in text.lower()]
 
    def filter_by_keywords(df, keywords):
        if not keywords:
            return pd.DataFrame()
        pattern = "|".join(keywords)
        mask_service = df['Service_Type'].str.contains(pattern, case=False, na=False)
        mask_category = df['Category_New'].str.contains(pattern, case=False, na=False)
        return df[mask_service | mask_category]
 
 
    def chunk_dataframe(df, max_chars=MAX_CHARS):
        chunks = []
        header = "| " + " | ".join(df.columns) + " |\n"
        divider = "| " + " | ".join(["---"] * len(df.columns)) + " |\n"
        current_chunk = header + divider
 
        for _, row in df.iterrows():
            row_str = "| " + " | ".join(str(cell) for cell in row) + " |\n"
            if len(current_chunk) + len(row_str) > max_chars:
                chunks.append(current_chunk)
                current_chunk = header + divider + row_str
            else:
                current_chunk += row_str
 
        if current_chunk.strip() != header.strip() + divider.strip():
            chunks.append(current_chunk)
 
        return chunks
 
    def build_prompt(user_input, context_chunk, keywords):
        return f"""Here is data related to {', '.join(keywords)}:\n{context_chunk}\n\nUser said: {user_input}"""
   
 
 
    if __name__ == "__main__":
        pass