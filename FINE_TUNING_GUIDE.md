# Fine-Tuning Guide for AI Comedy Lab

Complete guide to fine-tuning a custom model on Tamil comedian dialogues.

## Overview

Fine-tuning creates a specialized version of a base model (like GPT-3.5-turbo) that's trained on your specific data. Unlike RAG which retrieves information or system prompts which provide instructions, fine-tuning actually modifies the model's neural network weights.

## Prerequisites

1. ✅ Completed basic setup (database, embeddings, etc.)
2. ✅ OpenRouter API key with fine-tuning access
3. ✅ At least 50-100 dialogue examples (more is better)
4. ✅ Budget for fine-tuning costs (~$0.08 per 10K tokens)

## Step-by-Step Process

### Step 1: Expand Your Dataset (IMPORTANT!)

Currently you have only **15 dialogues**. You need **at least 50+** for decent results, ideally **100-200+**.

**Add more dialogues to your JSON files:**

```bash
# Edit these files:
data/raw/vadivelu_dialogues.json
data/raw/santhanam_dialogues.json
data/raw/vivek_dialogues.json
```

**Example of what to add:**

```json
{
  "comedian": "vadivelu",
  "movie_name": "Dhool",
  "year": 2003,
  "character_name": "Inspector",
  "scene_description": "Vadivelu interrogating a suspect with comedy",
  "dialogue_tamil": "உன் பேரு என்ன?",
  "dialogue_english": "What's your name? Actually, don't tell me, I'll guess it from your face!",
  "context": "Using exaggerated detective work for comedy",
  "emotion": "comedy_sarcasm",
  "metadata": {
    "tags": ["interrogation", "sarcasm", "detective"]
  }
}
```

**Tips for creating good training data:**
- Include diverse scenarios (traffic, marriage, food, work, etc.)
- Mix different emotions (comedy, sarcasm, wisdom, anger)
- Include both famous quotes and lesser-known dialogues
- Ensure English translations are accurate
- Add rich context descriptions

### Step 2: Import New Dialogues

After adding 50+ dialogues per comedian:

```bash
# Activate virtual environment
source venv/bin/activate

# Import dialogues into database
python scripts/populate_data.py

# Generate embeddings (for RAG, but good to have)
python scripts/generate_embeddings.py
```

### Step 3: Prepare Fine-Tuning Dataset

Convert dialogues to OpenAI fine-tuning format:

```bash
python scripts/prepare_fine_tuning.py
```

This creates `data/processed/fine_tuning_dataset.jsonl` with format:

```jsonl
{"messages":[{"role":"system","content":"You are Vadivelu..."},{"role":"user","content":"Tell me about marriage"},{"role":"assistant","content":"Marriage-a? Enna koduma sir idhu!"}]}
```

**Check your dataset:**

```bash
# Count training examples
wc -l data/processed/fine_tuning_dataset.jsonl

# View first few examples
head -3 data/processed/fine_tuning_dataset.jsonl
```

### Step 4: Check Dataset Stats (via API)

```bash
curl http://localhost:5000/fine-tuning/dataset-stats
```

Response shows:
- Number of training examples
- Whether you have enough data
- Recommendations

### Step 5: Start Fine-Tuning Job

**Option A: Using cURL**

```bash
curl -X POST http://localhost:5000/fine-tuning/start \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "tamil_comedian_v1",
    "hyperparameters": {
      "n_epochs": 3,
      "batch_size": 4,
      "learning_rate_multiplier": 0.1
    }
  }'
```

**Option B: Using Python**

```python
import requests

response = requests.post(
    'http://localhost:5000/fine-tuning/start',
    json={
        'model_name': 'tamil_comedian_v1',
        'hyperparameters': {
            'n_epochs': 3,  # More epochs = more training
            'batch_size': 4,
            'learning_rate_multiplier': 0.1
        }
    }
)

result = response.json()
print(f"Job ID: {result['job_id']}")
print(f"Status: {result['status']}")
```

**Response:**

```json
{
  "success": true,
  "job_id": "ftjob-abc123",
  "model_name": "tamil_comedian_v1",
  "status": "pending",
  "message": "Fine-tuning job started successfully",
  "next_steps": [
    "Monitor status: GET /fine-tuning/status/ftjob-abc123",
    "Fine-tuning typically takes 10-60 minutes depending on dataset size",
    "You will receive an email when training completes"
  ]
}
```

### Step 6: Monitor Training Progress

**Check job status:**

```bash
curl http://localhost:5000/fine-tuning/status/ftjob-abc123
```

**Response:**

```json
{
  "job_id": "ftjob-abc123",
  "status": "running",  // pending → running → succeeded/failed
  "model_name": "tamil_comedian_v1",
  "base_model": "openai/gpt-3.5-turbo",
  "fine_tuned_model": null,  // Will be populated when complete
  "created_at": "2024-01-15T10:30:00",
  "finished_at": null,
  "trained_tokens": 5000,
  "status_explanation": "Model is currently training on your data"
}
```

**Status progression:**
1. `validating_files` - Checking your data format
2. `queued` - Waiting for training resources
3. `running` - Actively training (10-60 minutes)
4. `succeeded` - Training complete! ✅
5. `failed` - Something went wrong ❌

### Step 7: Use Your Fine-Tuned Model

Once status is `succeeded`, you'll get a model ID like:
`ft:gpt-3.5-turbo:org:tamil_comedian_v1:abc123`

**Chat with fine-tuned model:**

```bash
curl -X POST http://localhost:5000/fine-tuning/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "ft:gpt-3.5-turbo:org:tamil_comedian_v1:abc123",
    "message": "Tell me a joke about Chennai traffic"
  }'
```

**Response:**

```json
{
  "response": "Chennai traffic-la stuck aayiten! Morning-la start panninen, evening aagiduchi!",
  "model": "ft:gpt-3.5-turbo:org:tamil_comedian_v1:abc123",
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 25,
    "total_tokens": 40
  }
}
```

### Step 8: Compare Base vs Fine-Tuned

See the difference between base model and your fine-tuned model:

```bash
curl -X POST http://localhost:5000/fine-tuning/compare \
  -H "Content-Type: application/json" \
  -d '{
    "fine_tuned_model": "ft:gpt-3.5-turbo:org:tamil_comedian_v1:abc123",
    "prompt": "What do you think about marriage?"
  }'
```

**Response shows side-by-side comparison:**

```json
{
  "comparison": {
    "prompt": "What do you think about marriage?",
    "base_model": {
      "model": "openai/gpt-3.5-turbo",
      "response": "Marriage is a commitment between two people..."
    },
    "fine_tuned": {
      "model": "ft:gpt-3.5-turbo:org:tamil_comedian_v1:abc123",
      "response": "Marriage-a? Enna koduma sir idhu! One minute proposal, lifetime tension!"
    }
  },
  "analysis": {
    "base_model_note": "Generic response from base model",
    "fine_tuned_note": "Specialized response using Vadivelu's style!"
  }
}
```

## Hyperparameters Explained

```json
{
  "n_epochs": 3,              // How many times to train on full dataset
                              // More = better learning, but risk overfitting
                              // Recommended: 3-4 for 50+ examples

  "batch_size": 4,            // Examples processed together
                              // Smaller = more stable, slower
                              // Recommended: 4-8

  "learning_rate_multiplier": 0.1  // How much to update weights
                                    // Smaller = safer, slower learning
                                    // Recommended: 0.05-0.2
}
```

## Cost Estimation

**Training Costs (one-time):**
- GPT-3.5-turbo: ~$0.008 per 1,000 tokens
- 100 dialogues ≈ 10,000 tokens ≈ **$0.08**
- 200 dialogues ≈ 20,000 tokens ≈ **$0.16**

**Usage Costs (ongoing):**
- Fine-tuned models cost same as base model
- GPT-3.5-turbo: $0.0005/1K input, $0.0015/1K output

## Troubleshooting

### "Training file not found"

```bash
# Make sure you ran:
python scripts/prepare_fine_tuning.py

# Check if file exists:
ls -lh data/processed/fine_tuning_dataset.jsonl
```

### "Not enough training examples"

You need **minimum 10 examples**, recommended **50+**:

```bash
# Check count:
wc -l data/processed/fine_tuning_dataset.jsonl

# Add more dialogues to JSON files, then:
python scripts/populate_data.py
python scripts/prepare_fine_tuning.py
```

### "Fine-tuning job failed"

Common reasons:
1. **Invalid JSONL format** - Each line must be valid JSON
2. **Insufficient data** - Need at least 10 examples
3. **API key lacks fine-tuning access** - Check OpenRouter permissions
4. **Model doesn't support fine-tuning** - Use GPT-3.5-turbo or GPT-4

### "Model not learning comedian style"

1. **Add more diverse examples** - Need 100+ for good results
2. **Increase epochs** - Try `n_epochs: 4`
3. **Better training data** - Include more varied scenarios
4. **Check data quality** - Ensure dialogues are actually in comedian's style

## Best Practices

### Data Quality
- ✅ Use actual movie dialogues, not generated content
- ✅ Include both Tamil and English for context
- ✅ Add rich scene descriptions
- ✅ Tag emotions accurately
- ❌ Don't use too-similar examples (avoid duplicates)
- ❌ Don't mix comedian styles in one example

### Training Strategy
- **Start small**: Test with 50 examples first
- **Iterate**: Train → Test → Add more data → Retrain
- **Validate**: Keep 10% of data for testing (don't include in training)
- **Monitor**: Check if model is overfitting (memorizing vs learning)

### Model Naming
Use descriptive names:
- ✅ `vadivelu_comedy_v1`
- ✅ `tamil_comedians_mixed_v2`
- ✅ `santhanam_modern_v1`
- ❌ `model1`, `test`, `final`

## Advanced: Training Different Models

### Comedian-Specific Models

Train separate models for each comedian:

```bash
# Modify prepare_fine_tuning.py to filter by comedian
# Then train 3 separate models:

# Vadivelu only
python scripts/prepare_fine_tuning.py --comedian vadivelu
curl -X POST .../fine-tuning/start -d '{"model_name": "vadivelu_v1"}'

# Santhanam only
python scripts/prepare_fine_tuning.py --comedian santhanam
curl -X POST .../fine-tuning/start -d '{"model_name": "santhanam_v1"}'

# Vivek only
python scripts/prepare_fine_tuning.py --comedian vivek
curl -X POST .../fine-tuning/start -d '{"model_name": "vivek_v1"}'
```

### Mixed Model

Train one model on all comedians (current default):

```bash
python scripts/prepare_fine_tuning.py  # Includes all comedians
curl -X POST .../fine-tuning/start -d '{"model_name": "tamil_comedy_v1"}'
```

## Educational Value

**For students, demonstrate:**

1. **Data Preparation** - Show JSONL format, data quality importance
2. **Training Process** - Explain epochs, learning rates, overfitting
3. **Comparison** - Show base vs fine-tuned responses side-by-side
4. **Trade-offs** - Discuss when to use fine-tuning vs RAG vs prompts

## Next Steps After Fine-Tuning

1. **Create UI** - Build a comparison dashboard
2. **A/B Testing** - Compare fine-tuned vs RAG vs prompts
3. **Metrics** - Track response quality, coherence, style accuracy
4. **Expand** - Add more comedians, more dialogues
5. **Production** - Deploy fine-tuned model in your app

## Summary: Quick Command Reference

```bash
# 1. Add dialogues to data/raw/*.json files

# 2. Import and prepare
python scripts/populate_data.py
python scripts/prepare_fine_tuning.py

# 3. Check dataset
curl http://localhost:5000/fine-tuning/dataset-stats

# 4. Start training
curl -X POST http://localhost:5000/fine-tuning/start \
  -H "Content-Type: application/json" \
  -d '{"model_name": "comedian_v1"}'

# 5. Monitor progress
curl http://localhost:5000/fine-tuning/status/JOB_ID

# 6. Use fine-tuned model (when complete)
curl -X POST http://localhost:5000/fine-tuning/chat \
  -H "Content-Type: application/json" \
  -d '{"model_id": "ft:...", "message": "your question"}'

# 7. Compare results
curl -X POST http://localhost:5000/fine-tuning/compare \
  -H "Content-Type: application/json" \
  -d '{"fine_tuned_model": "ft:...", "prompt": "test"}'
```

---

**Ready to start?** Add 50+ more dialogues to your JSON files and follow the steps above! 🚀
