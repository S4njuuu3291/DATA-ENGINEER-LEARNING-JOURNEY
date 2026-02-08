"""
E2E TESTING - End-to-End Pipeline Testing

Topics:
- Testing complete data pipelines
- Output validation strategies
- Automated quality checks
- Test data management
- CI/CD integration patterns

Cara run:
    pytest 6-e2e-testing.py -v
    
Production pattern untuk validate entire workflows.
"""

import pytest
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
import tempfile
import shutil

# ==========================================
# SAMPLE ETL PIPELINE (To Test)
# ==========================================

class DataPipeline:
    """
    Complete ETL pipeline - dari extract sampai load.
    
    This is what we want to test end-to-end.
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.temp_dir = Path(config.get('temp_dir', '/tmp/pipeline'))
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def extract(self, source: str) -> pd.DataFrame:
        """Extract data dari source."""
        if source == 'api':
            # Simulate API call
            data = {
                'id': [1, 2, 3, 4, 5],
                'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
                'score': [95, 88, 92, None, 85],
                'created_at': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05']
            }
            return pd.DataFrame(data)
        elif source == 'file':
            # Simulate file read
            return pd.read_csv(self.config['input_file'])
        else:
            raise ValueError(f"Unknown source: {source}")
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform data with business logic."""
        # 1. Handle missing values
        df['score'] = df['score'].fillna(df['score'].mean())
        
        # 2. Add calculated fields
        df['grade'] = df['score'].apply(self._calculate_grade)
        
        # 3. Convert dates
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        # 4. Add metadata
        df['processed_at'] = datetime.now()
        df['pipeline_version'] = '1.0.0'
        
        return df
    
    def validate(self, df: pd.DataFrame) -> Dict[str, any]:
        """Validate data quality."""
        checks = {
            'total_records': len(df),
            'null_scores': df['score'].isnull().sum(),
            'null_names': df['name'].isnull().sum(),
            'score_range_valid': ((df['score'] >= 0) & (df['score'] <= 100)).all(),
            'all_grades_valid': df['grade'].isin(['A', 'B', 'C', 'D', 'F']).all()
        }
        
        # Check if validation passed
        checks['validation_passed'] = (
            checks['null_scores'] == 0 and
            checks['null_names'] == 0 and
            checks['score_range_valid'] and
            checks['all_grades_valid']
        )
        
        return checks
    
    def load(self, df: pd.DataFrame, destination: str) -> str:
        """Load data ke destination."""
        if destination == 'parquet':
            output_path = self.temp_dir / 'output.parquet'
            df.to_parquet(output_path, index=False)
            return str(output_path)
        elif destination == 'csv':
            output_path = self.temp_dir / 'output.csv'
            df.to_csv(output_path, index=False)
            return str(output_path)
        elif destination == 'json':
            output_path = self.temp_dir / 'output.json'
            df.to_json(output_path, orient='records', date_format='iso')
            return str(output_path)
        else:
            raise ValueError(f"Unknown destination: {destination}")
    
    def run(self, source: str = 'api', destination: str = 'parquet') -> Dict[str, any]:
        """Run complete pipeline."""
        # Extract
        df_raw = self.extract(source)
        
        # Transform
        df_transformed = self.transform(df_raw)
        
        # Validate
        validation_results = self.validate(df_transformed)
        
        if not validation_results['validation_passed']:
            raise ValueError(f"Validation failed: {validation_results}")
        
        # Load
        output_path = self.load(df_transformed, destination)
        
        return {
            'status': 'success',
            'records_processed': len(df_transformed),
            'output_path': output_path,
            'validation': validation_results
        }
    
    @staticmethod
    def _calculate_grade(score: float) -> str:
        """Calculate letter grade from score."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def cleanup(self):
        """Cleanup temporary files."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

# ==========================================
# FIXTURES untuk E2E Testing
# ==========================================

@pytest.fixture(scope='function')
def temp_workspace():
    """Create temporary workspace untuk testing."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_input_data(temp_workspace):
    """Create sample input CSV file."""
    data = {
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'score': [95, 88, 92],
        'created_at': ['2024-01-01', '2024-01-02', '2024-01-03']
    }
    df = pd.DataFrame(data)
    
    input_file = temp_workspace / 'input.csv'
    df.to_csv(input_file, index=False)
    
    return input_file

@pytest.fixture
def pipeline_config(temp_workspace, sample_input_data):
    """Pipeline configuration."""
    return {
        'temp_dir': str(temp_workspace),
        'input_file': str(sample_input_data),
        'output_format': 'parquet'
    }

@pytest.fixture
def pipeline(pipeline_config):
    """Initialize pipeline."""
    pipeline = DataPipeline(pipeline_config)
    yield pipeline
    pipeline.cleanup()

# ==========================================
# E2E TEST SUITE
# ==========================================

class TestPipelineE2E:
    """End-to-end testing untuk complete pipeline."""
    
    def test_complete_pipeline_success(self, pipeline):
        """Test: Complete pipeline runs successfully."""
        # Run entire pipeline
        result = pipeline.run(source='api', destination='parquet')
        
        # Verify overall success
        assert result['status'] == 'success'
        assert result['records_processed'] > 0
        assert Path(result['output_path']).exists()
        
        # Verify validation passed
        assert result['validation']['validation_passed'] is True
    
    def test_output_file_contents(self, pipeline):
        """Test: Output file contains expected data."""
        # Run pipeline
        result = pipeline.run(source='api', destination='parquet')
        
        # Read output
        df_output = pd.read_parquet(result['output_path'])
        
        # Verify structure
        assert len(df_output) == 5  # 5 records
        assert 'grade' in df_output.columns
        assert 'processed_at' in df_output.columns
        
        # Verify transformations applied
        assert df_output['score'].isnull().sum() == 0  # No nulls after fillna
        assert all(df_output['grade'].isin(['A', 'B', 'C', 'D', 'F']))
    
    def test_data_quality_checks(self, pipeline):
        """Test: All data quality checks pass."""
        result = pipeline.run(source='api', destination='parquet')
        
        validation = result['validation']
        
        # All quality checks
        assert validation['null_scores'] == 0
        assert validation['null_names'] == 0
        assert validation['score_range_valid'] is True
        assert validation['all_grades_valid'] is True
        assert validation['total_records'] == 5
    
    def test_different_output_formats(self, pipeline):
        """Test: Pipeline supports multiple output formats."""
        formats = ['parquet', 'csv', 'json']
        
        for fmt in formats:
            result = pipeline.run(source='api', destination=fmt)
            
            # File created
            assert Path(result['output_path']).exists()
            
            # Read and verify
            if fmt == 'parquet':
                df = pd.read_parquet(result['output_path'])
            elif fmt == 'csv':
                df = pd.read_csv(result['output_path'])
            elif fmt == 'json':
                df = pd.read_json(result['output_path'])
            
            assert len(df) == 5
            assert 'grade' in df.columns
    
    def test_pipeline_with_file_source(self, pipeline):
        """Test: Pipeline can extract dari file."""
        result = pipeline.run(source='file', destination='parquet')
        
        # Success
        assert result['status'] == 'success'
        assert result['records_processed'] == 3  # From sample_input_data
    
    def test_pipeline_metadata(self, pipeline):
        """Test: Pipeline adds correct metadata."""
        result = pipeline.run(source='api', destination='parquet')
        
        df = pd.read_parquet(result['output_path'])
        
        # Check metadata columns exist
        assert 'processed_at' in df.columns
        assert 'pipeline_version' in df.columns
        
        # Check values
        assert df['pipeline_version'].iloc[0] == '1.0.0'
        assert pd.notna(df['processed_at'].iloc[0])
    
    def test_grade_calculation_logic(self, pipeline):
        """Test: Grade calculation is correct."""
        result = pipeline.run(source='api', destination='parquet')
        df = pd.read_parquet(result['output_path'])
        
        # Check specific grades
        alice = df[df['name'] == 'Alice'].iloc[0]
        assert alice['score'] == 95
        assert alice['grade'] == 'A'
        
        bob = df[df['name'] == 'Bob'].iloc[0]
        assert bob['score'] == 88
        assert bob['grade'] == 'B'
    
    def test_null_handling(self, pipeline):
        """Test: Null values are properly handled."""
        # Extract
        df_raw = pipeline.extract('api')
        
        # Check raw data has nulls
        assert df_raw['score'].isnull().sum() > 0
        
        # Transform
        df_transformed = pipeline.transform(df_raw)
        
        # Check nulls are filled
        assert df_transformed['score'].isnull().sum() == 0

# ==========================================
# INTEGRATION TESTS (Partial Pipeline)
# ==========================================

class TestPipelineIntegration:
    """Test individual components dalam integration context."""
    
    def test_extract_transform_integration(self, pipeline):
        """Test: Extract → Transform flow."""
        # Extract
        df_raw = pipeline.extract('api')
        assert len(df_raw) > 0
        
        # Transform
        df_transformed = pipeline.transform(df_raw)
        assert 'grade' in df_transformed.columns
        assert len(df_transformed) == len(df_raw)
    
    def test_transform_validate_integration(self, pipeline):
        """Test: Transform → Validate flow."""
        # Extract & Transform
        df_raw = pipeline.extract('api')
        df_transformed = pipeline.transform(df_raw)
        
        # Validate
        validation = pipeline.validate(df_transformed)
        assert validation['validation_passed'] is True
    
    def test_transform_load_integration(self, pipeline):
        """Test: Transform → Load flow."""
        # Extract & Transform
        df_raw = pipeline.extract('api')
        df_transformed = pipeline.transform(df_raw)
        
        # Load
        output_path = pipeline.load(df_transformed, 'parquet')
        
        # Verify file
        assert Path(output_path).exists()
        df_loaded = pd.read_parquet(output_path)
        assert len(df_loaded) == len(df_transformed)

# ==========================================
# AUTOMATED VALIDATION SCRIPTS
# ==========================================

class TestAutomatedValidation:
    """Automated validation checks untuk production."""
    
    def test_schema_validation(self, pipeline):
        """Test: Output schema matches expected."""
        result = pipeline.run(source='api', destination='parquet')
        df = pd.read_parquet(result['output_path'])
        
        # Expected schema
        expected_columns = ['id', 'name', 'score', 'created_at', 'grade', 'processed_at', 'pipeline_version']
        
        # Verify all columns present
        for col in expected_columns:
            assert col in df.columns, f"Missing column: {col}"
    
    def test_data_type_validation(self, pipeline):
        """Test: Output data types are correct."""
        result = pipeline.run(source='api', destination='parquet')
        df = pd.read_parquet(result['output_path'])
        
        # Check types
        assert df['id'].dtype in ['int64', 'int32']
        assert df['name'].dtype == 'object'  # string
        assert df['score'].dtype in ['float64', 'float32']
        assert pd.api.types.is_datetime64_any_dtype(df['created_at'])
    
    def test_data_completeness(self, pipeline):
        """Test: No missing required fields."""
        result = pipeline.run(source='api', destination='parquet')
        df = pd.read_parquet(result['output_path'])
        
        # Required fields
        required_fields = ['id', 'name', 'score', 'grade']
        
        for field in required_fields:
            null_count = df[field].isnull().sum()
            assert null_count == 0, f"Field {field} has {null_count} nulls"
    
    def test_business_rules_validation(self, pipeline):
        """Test: Business rules are enforced."""
        result = pipeline.run(source='api', destination='parquet')
        df = pd.read_parquet(result['output_path'])
        
        # Rule 1: Scores in valid range
        assert (df['score'] >= 0).all()
        assert (df['score'] <= 100).all()
        
        # Rule 2: Grades match scores
        for _, row in df.iterrows():
            expected_grade = pipeline._calculate_grade(row['score'])
            assert row['grade'] == expected_grade
        
        # Rule 3: Created date not in future
        assert (df['created_at'] <= pd.Timestamp.now()).all()
    
    def test_record_count_validation(self, pipeline):
        """Test: Record count dalam expected range."""
        result = pipeline.run(source='api', destination='parquet')
        
        # Check count
        count = result['records_processed']
        
        # Business rule: Expect 3-10 records untuk API source
        assert 3 <= count <= 10, f"Unexpected record count: {count}"

# ==========================================
# BEST PRACTICES
# ==========================================

"""
✅ E2E Testing Best Practices:

1. TEST ENTIRE WORKFLOW:
   - Test complete pipeline dari extract sampai load
   - Verify output files actually created
   - Check actual data dalam output

2. VALIDATE DATA QUALITY:
   - Schema validation
   - Data type validation
   - Business rules validation
   - Completeness checks

3. USE REALISTIC DATA:
   - Test with production-like volumes (sample)
   - Include edge cases (nulls, invalid values)
   - Test different input formats

4. AUTOMATE VALIDATION:
   - Create reusable validation functions
   - Run as part of CI/CD
   - Alert on failures

5. TEST IDEMPOTENCY:
   - Pipeline should be runnable multiple times
   - Same input → same output
   - Proper cleanup

❌ Common Mistakes:

1. Only testing individual functions (need E2E too!)
2. Not validating actual output files
3. Using toy data (not realistic)
4. Ignoring data quality checks
5. Not testing error scenarios

📊 Test Organization:

tests/
├── unit/               # Individual functions
├── integration/        # Component interactions
└── e2e/               # Complete workflows
    ├── test_pipeline_e2e.py
    ├── test_data_quality.py
    └── fixtures/
        ├── input_samples/
        └── expected_outputs/

🎯 When to Use E2E Tests:

✅ Use for:
- Validating complete pipeline functionality
- Regression testing sebelum deploy
- CI/CD pipeline validation
- Production smoke tests

❌ Don't use for:
- Quick iterative development (too slow)
- Debugging individual functions (use unit tests)
- Testing external services (use integration tests)

🔗 Next Steps:

1. Add more validation checks
2. Implement CI/CD integration
3. Add performance benchmarks
4. Create production monitoring
"""

if __name__ == "__main__":
    pytest.main([__file__, '-v'])
