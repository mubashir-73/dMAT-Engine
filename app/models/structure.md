Ah — **this image changes my recommendation slightly**.

Looking at the three actual dMAT screens, the important thing isn't merely that questions contain text/images/equations. The bigger point is:

> **The three core modules have fundamentally different interaction models.**

And because your MVP is specifically about reproducing the **look and feel of the dMAT test**, I would **not** try to force all three into a generic "question + options" abstraction.

You want a **question record + module-specific JSON configuration**.

---

# What the screenshots actually show

### 1. Figure Sequences

You have:

```text
Question
 ├── sequence of images
 └── answer options
       ├── image
       ├── image
       ├── image
       └── image
```

The user isn't answering with text. They're selecting a **figure**.

---

### 2. Latin Squares

This is quite different.

```text
Question
 ├── grid
 ├── letters/numbers placed in grid
 ├── missing cell
 └── answer column
       ├── A
       ├── B
       ├── C
       ├── D
       └── E
```

So the "options" aren't really ordinary option objects containing text/images. They are part of the **Latin-square interaction UI**.

---

### 3. Mathematical Equations

This one has **no options at all**.

```text
Question
 ├── equations
 └── answer inputs
       ├── A = [input]
       ├── B = [input]
       ├── C = [input]
       └── D = [input]
```

The student enters values.

So trying to make this:

```text
Question
 ├── text
 ├── options[]
 └── correct_option
```

would be a bad abstraction.

---

# For your MVP, I'd use this

```text
                    ┌────────────────────┐
                    │      Question      │
                    ├────────────────────┤
                    │ id                 │
                    │ module_type        │
                    │ difficulty         │
                    │ data JSONB         │
                    │ solution JSONB     │
                    └─────────┬──────────┘
                              │
              ┌───────────────┼────────────────┐
              ↓               ↓                ↓
       FIGURE_SEQUENCE   LATIN_SQUARE   MATHEMATICAL_EQUATION
```

This is much cleaner for what you're actually building.

---

# 1. `questions`

I'd make the core table very small.

```sql
questions
---------
id
module_type
difficulty
data
solution
created_at
updated_at
```

Where:

```text
module_type
-----------
FIGURE_SEQUENCE
LATIN_SQUARE
MATHEMATICAL_EQUATION
```

You can later add:

```text
SUBJECT
```

for the subject modules.

---

# 2. `data` is the question-specific configuration

This is where PostgreSQL's `JSONB` becomes extremely useful.

You don't need 15 tables to represent three completely different question types.

---

## Figure Sequence

Something like:

```json
{
  "type": "figure_sequence",

  "sequence": [
    {
      "asset_id": "img_001"
    },
    {
      "asset_id": "img_002"
    },
    {
      "asset_id": "img_003"
    },
    {
      "asset_id": "img_004"
    }
  ],

  "options": [
    {
      "id": "A",
      "asset_id": "img_101"
    },
    {
      "id": "B",
      "asset_id": "img_102"
    },
    {
      "id": "C",
      "asset_id": "img_103"
    },
    {
      "id": "D",
      "asset_id": "img_104"
    }
  ]
}
```

Then:

```json
{
  "correct_option": "C"
}
```

goes into `solution`.

---

# 3. Latin Square

This is where the JSON approach becomes really nice.

```json
{
  "type": "latin_square",

  "grid": {
    "rows": 5,
    "columns": 5,

    "cells": [
      ["", "", "", "", ""],
      ["", "", "", "", ""],
      ["A", "B", "E", null, ""],
      ["", "D", "", "", ""],
      ["", "", "", "", "C"]
    ]
  },

  "missing_cell": {
    "row": 2,
    "column": 3
  },

  "options": [
    { "id": "A" },
    { "id": "B" },
    { "id": "C" },
    { "id": "D" },
    { "id": "E" }
  ]
}
```

Then:

```json
{
  "correct_option": "D"
}
```

The frontend knows:

```text
module_type = LATIN_SQUARE
```

and therefore renders the Latin Square component.

---

# 4. Mathematical Equations

Now we don't need `options` whatsoever.

```json
{
  "type": "mathematical_equation",

  "equations": ["A - B + C - D = 2", "10 × B = C", "5 × B = A", "11 + B = D"],

  "variables": ["A", "B", "C", "D"]
}
```

And:

```json
{
  "answers": {
    "A": 5,
    "B": 1,
    "C": 10,
    "D": 12
  }
}
```

Your frontend then knows:

```text
A = [input]
B = [input]
C = [input]
D = [input]
```

No fake options table required.

---

# This gives you a really clean frontend architecture

Your API could return:

```json
{
  "id": "q_123",
  "module_type": "FIGURE_SEQUENCE",
  "difficulty": 3,
  "data": {
    ...
  }
}
```

React:

```tsx
switch (question.module_type) {
  case "FIGURE_SEQUENCE":
    return <FigureSequenceQuestion question={question} />;

  case "LATIN_SQUARE":
    return <LatinSquareQuestion question={question} />;

  case "MATHEMATICAL_EQUATION":
    return <MathematicalEquationQuestion question={question} />;
}
```

That's **exactly what you want for an MVP**.

You're not building a generic exam SaaS platform. You're building a **dMAT replica/practice engine**.

Don't abstract yourself into oblivion.

---

# What about images?

I'd still have an `assets` table.

```text
assets
------
id
storage_key
mime_type
width
height
```

Then:

```json
{
  "asset_id": "img_001"
}
```

references the actual image.

For your MVP, those images could simply live in:

```text
MinIO
```

or even a local/static directory initially.

You don't need S3 infrastructure just to prove the test engine works.

---

# The important part: `solution` should be separate

This is **very important**.

Don't send this to the browser:

```json
{
  "data": {...},
  "solution": {
    "correct_option": "C"
  }
}
```

Otherwise someone opens DevTools and congratulations, they've become the world's greatest dMAT candidate. 😂

Instead your database has:

```text
questions
────────────────────────────
id
module_type
difficulty
data
solution
```

But your API has two representations:

### Student

```json
{
  "id": "q123",
  "module_type": "FIGURE_SEQUENCE",
  "difficulty": 2,
  "data": {
    "sequence": [...],
    "options": [...]
  }
}
```

### Server internally

```json
{
  "correct_option": "C"
}
```

When the student submits:

```http
POST /test/questions/q123/answer
```

```json
{
  "answer": {
    "selected_option": "C"
  }
}
```

Backend compares it against `solution`.

---

# And this solves your "different options" problem

Your concern was essentially:

> "What if one question has image options, another has text options, another has no options?"

With this architecture:

### Figure sequence

```json
{
  "type": "figure_sequence",
  "options": [
    { "id": "A", "asset_id": "..." },
    { "id": "B", "asset_id": "..." }
  ]
}
```

### Latin square

```json
{
  "type": "latin_square",
  "options": [{ "id": "A" }, { "id": "B" }, { "id": "C" }]
}
```

### Equations

```json
{
  "type": "mathematical_equation",
  "variables": ["A", "B", "C", "D"]
}
```

No `options` whatsoever.

**That's completely fine.**

---

# I would NOT create these tables

For your MVP, avoid:

```text
question_options
question_images
question_equations
question_text
question_tables
question_figures
equation_answers
latin_square_cells
figure_sequence_frames
...
```

That is massive overengineering for what you're trying to demonstrate.

You'd spend more time designing the database than actually making the test engine.

---

# Your SQLAlchemy model could literally be this simple

Something along these lines:

```python
class Question(Base):
    __tablename__ = "questions"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    module_type: Mapped[QuestionModule] = mapped_column(
        Enum(QuestionModule),
        nullable=False,
    )

    difficulty: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    data: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    solution: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )
```

And:

```python
class QuestionModule(str, Enum):
    FIGURE_SEQUENCE = "figure_sequence"
    LATIN_SQUARE = "latin_square"
    MATHEMATICAL_EQUATION = "mathematical_equation"
```

That's basically enough for the **question bank**.

---

# One thing I'd add: `render_type`

There's a subtle distinction I'd make.

Don't make your frontend infer everything from `module_type`.

You can have:

```text
module_type
    ↓
What kind of dMAT question is this?

render_type
    ↓
How should the test UI render it?
```

For your current three:

```text
module_type             render_type

FIGURE_SEQUENCE         FIGURE_SEQUENCE
LATIN_SQUARE            LATIN_SQUARE
MATHEMATICAL_EQUATION   EQUATION_INPUT
```

But honestly, for the MVP you can skip this and just use `module_type`. Add it only if you actually encounter a case where two questions from the same module need different renderers.

---

# What your final MVP schema could look like

I'd aim for this:

```text
                         ┌──────────────┐
                         │   subjects   │
                         └──────┬───────┘
                                │
                         ┌──────▼───────┐
                         │   questions  │
                         ├──────────────┤
                         │ id           │
                         │ module_type  │
                         │ difficulty   │
                         │ data JSONB   │
                         │ solution     │
                         └──────┬───────┘
                                │
                         references
                                │
                         ┌──────▼───────┐
                         │    assets    │
                         ├──────────────┤
                         │ id           │
                         │ storage_key  │
                         │ mime_type    │
                         └──────────────┘
```

Then your **test/session tables remain separate**:

```text
Test
 │
 ├── TestQuestions
 │       │
 │       └── Question
 │
 └── Attempt
         │
         └── Answers
```

So the architecture becomes:

```text
QUESTION BANK
     │
     │
     ▼
┌───────────────┐
│   Questions   │
│               │
│ JSONB content │
└───────┬───────┘
        │
        ▼
   Test Generator
        │
        ▼
    Test Session
        │
        ▼
      Student
```

## My recommendation for your exact MVP

**Use relational columns for things you need to query/filter:**

```text
id
module_type
difficulty
subject/topic
```

**Use JSONB for the actual module-specific question structure:**

```text
data
```

**Use a separate JSONB solution for answer verification:**

```text
solution
```

**Use an asset table/storage for images.**

And most importantly, **don't try to make all three core modules look like MCQs in the database**. The screenshots show that they aren't. Your database should represent the _behavioral model_ of each module, while your React components reproduce the actual dMAT UI.

For the MVP, this is probably the sweet spot between **"hacky JSON blob"** and **"enterprise question-management ontology from hell."**
