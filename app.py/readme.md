# Novateach.ai

Novateach.ai is an adaptive learning system designed to generate personalized educational
lectures based on a student's learner profile, topic, academic level, and difficulty.

The core idea is not simply to generate AI videos.

Novateach maintains a learner model, uses that model to plan instruction, generates a
structured lecture, evaluates the student's understanding through a quiz, and updates
the learner model for future lessons.

---

## Core Learning Loop

Student
↓
Learner Profile
↓
Lesson Planning
↓
Lecture Production
↓
TTS + Visual Generation
↓
Final Educational Video
↓
Quiz
↓
Quiz Analysis
↓
Updated Learner Profile
↓
Next Personalized Lesson

The learner profile is therefore not static.

It evolves after every completed lecture and quiz.

---

## System Architecture

Novateach is divided into separate stages.

Each stage has one responsibility and communicates with the next stage through structured
data contracts.

```text
                         STUDENT
                            │
                            ↓
                    LEARNER PROFILE
                            │
                 Topic + Academic Level
                     + Difficulty
                            │
                            ↓
                 ┌────────────────────┐
                 │   LESSON PLANNER   │
                 │                    │
                 │ WHAT to teach      │
                 │ Why / sequence     │
                 │ Personalization    │
                 └─────────┬──────────┘
                           │
                           ↓
                   LEARNING BLUEPRINT
                           │
                           ↓
              ┌──────────────────────────┐
              │ LECTURE PRODUCTION       │
              │ PLANNER                  │
              │                          │
              │ HOW to teach             │
              │ Parts                    │
              │ Scenes                   │
              │ Narration                │
              │ Estimated timing         │
              └────────────┬─────────────┘
                           │
                           ↓
                      TTS ENGINE
                           │
                           ↓
                 ACTUAL AUDIO + DURATION
                           │
                           ↓
              ┌──────────────────────────┐
              │     VISUAL PLANNER       │
              │                          │
              │ What appears             │
              │ When it appears          │
              │ Animations               │
              │ Overlays                 │
              │ Transitions              │
              └────────────┬─────────────┘
                           │
                           ↓
                 VISUAL TIMELINE
                           │
                           ↓
              ┌──────────────────────────┐
              │     VISUAL CREATOR       │
              │                          │
              │ Create/find assets       │
              │ Render scenes            │
              │ Assemble visual video    │
              │                          │
              │ OUTPUT: SILENT MP4       │
              └────────────┬─────────────┘
                           │
                           ↓
                       SILENT MP4
                           │
                           │
                 TTS AUDIO ─┤
                           ↓
              ┌──────────────────────────┐
              │     FINAL COMPOSER       │
              │                          │
              │ Merge audio + video      │
              └────────────┬─────────────┘
                           │
                           ↓
                       FINAL MP4
                           │
                           ↓
                          QUIZ
                           │
                           ↓
                  PROFILE UPDATE
