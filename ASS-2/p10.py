import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

def generate_dashboard(csv_path, output_folder):
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        # Read the student marks data chunk-by-chunk to handle up to 1,000,000 records safely
        chunks = []
        for chunk in pd.read_csv(csv_path, chunksize=50000):
            # Clean missing data dynamically (fill missing subject scores with 0)
            subject_cols = [c for c in chunk.columns if c not in ['enrollment', 'name']]
            chunk[subject_cols] = chunk[subject_cols].fillna(0)
            chunks.append(chunk)
            
        df = pd.concat(chunks, ignore_index=True)
        subject_cols = [c for c in df.columns if c not in ['enrollment', 'name']]
        
        # Calculate row totals for analysis
        df['Total'] = df[subject_cols].sum(axis=1)
        df['Average'] = df[subject_cols].mean(axis=1)
        
        # Define explicit grade bucketing criteria
        def assign_grade(score):
            if score >= 90: return 'A'
            elif score >= 80: return 'B'
            elif score >= 70: return 'C'
            elif score >= 60: return 'D'
            else: return 'F'
            
        df['Grade'] = df['Average'].apply(assign_grade)
        
        # Export the fully cleaned student master record
        cleaned_csv_path = os.path.join(output_folder, "cleaned_marks.csv")
        df.drop(columns=['Total', 'Average', 'Grade']).to_csv(cleaned_csv_path, index=False)
        
        # Compute subject-level aggregate metrics matrix
        summary_data = []
        for sub in subject_cols:
            summary_data.append({
                'Subject': sub,
                'Min': df[sub].min(),
                'Max': df[sub].max(),
                'Average': df[sub].mean()
            })
        summary_df = pd.DataFrame(summary_data)
        summary_csv_path = os.path.join(output_folder, "summary.csv")
        summary_df.to_csv(summary_csv_path, index=False)
        
        # 1. Visualization Export: Grade Distribution Bar Chart
        plt.figure(figsize=(6, 4))
        grade_counts = df['Grade'].value_counts().reindex(['A', 'B', 'C', 'D', 'F'], fill_value=0)
        grade_counts.plot(kind='bar', color='skyblue', edgecolor='black')
        plt.title('Overall Grade Distribution')
        plt.xlabel('Grade')
        plt.ylabel('Number of Students')
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, "grade_distribution.png"), dpi=100)
        plt.close()
        
        # 2. Visualization Export: Subject-wise Performance Comparison Chart
        plt.figure(figsize=(8, 4))
        plt.bar(summary_df['Subject'], summary_df['Average'], color='lightgreen', edgecolor='black')
        plt.title('Subject-wise Average Marks')
        plt.xlabel('Subjects')
        plt.ylabel('Average Score')
        plt.ylim(0, 100)
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, "subject_average.png"), dpi=100)
        plt.close()
        
        # 3. Visualization Export: Top Performers Ranking Chart
        plt.figure(figsize=(8, 4))
        top_performers = df.nlargest(10, 'Total')
        plt.barh(top_performers['name'][::-1], top_performers['Total'][::-1], color='gold', edgecolor='black')
        plt.title('Top 10 Performing Students')
        plt.xlabel('Total Cumulative Marks')
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, "top_performers.png"), dpi=100)
        plt.close()
        
    except Exception:
        return

if __name__ == "__main__":
    if len(sys.argv) > 2:
        generate_dashboard(sys.argv[1], sys.argv[2])
