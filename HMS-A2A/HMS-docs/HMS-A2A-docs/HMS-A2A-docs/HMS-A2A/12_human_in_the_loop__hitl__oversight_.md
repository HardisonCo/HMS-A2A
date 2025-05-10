# Chapter 12: Human-in-the-Loop (HITL) Oversight

*(From [AI Governance Values Layer](11_ai_governance_values_layer_.md) you saw how automated “values guards” block unsafe AI answers.  
But what if the bot’s answer is **legal** yet still *wrong*, *unclear*, or *politically sensitive*?  
Humans must have the last word.  
That safety net is called **Human-in-the-Loop (HITL) Oversight**.)*  

---

## 1. Why Do We Need HITL?  🛬

### Central Use-Case  
The **Small Business Administration (SBA)** runs an online **Loan-Forgiveness Portal**.  
An AI agent reviews each application and recommends one of three actions:

1. *Approve* – everything looks perfect.  
2. *Deny* – fraud indicators detected.  
3. *Request Docs* – missing payroll proof.

Congress, citizens, and inspectors expect that **a real loan officer** can:

* Double-check the AI’s recommendation.  
* Overrule it if needed.  
* See a crystal-clear audit trail of who did what, when, and why.

HITL makes this as easy as clicking “Approve,” “Edit,” or “Reject” in a queue—while logging every click forever.

---

## 2. Key Concepts in Plain English

| Term                | Beginner Analogy                               | Why It Matters |
|---------------------|------------------------------------------------|----------------|
| Decision Queue      | Inbox of AI suggestions                        | Officers work item-by-item |
| Override Button     | Big red “STOP” on the autopilot                | Lets humans change the AI outcome |
| Friction Counter    | “Number of arguments” with the AI              | Highlights models or officers needing retraining |
| Audit Stamp         | Tamper-proof diary entry                       | Accountability for IG audits |
| Escalation Trigger  | Seat-belt light that won’t turn off            | Forces review if friction is too high |

---

## 3. Where Does HITL Sit in HMS?

```
Citizen ↔ Portal ↔ AI Agent ↔ HITL Queue ↔ Human Officer
                                  │
                                  └─► Audit Trail (Governance Floor)
```

* The queue lives on the **Management Floor** (automatic but modifiable).  
* All clicks feed the **Governance Floor** audit store you met in earlier chapters.

---

## 4. Quick-Start: Add HITL to a Workflow in 3 Steps

We’ll extend the **FTC complaint workflow** from [Event & Workflow Orchestration](08_event___workflow_orchestration__hms_act___hms_oms__.md).

### 4.1  Declare a “reviewable” Step (YAML ≤15 lines)

```yaml
# workflows/ftc_complaint.yml  (snippet)
- id: classify
  actor: AI:fraud-labeler
  review: human                # ← NEW
  on_complete: notify_citizen
```

**What’s new?**  
`review: human` tells HMS-ACT to *pause* after the AI finishes and place a task in the HITL queue.

### 4.2  Minimal Officer UI (React ≤18 lines)

```tsx
// ReviewRow.tsx
export default function ReviewRow({task}) {
  function action(decision){
    fetch(`/act/tasks/${task.id}/override`,{
      method:'POST',headers:{'Content-Type':'application/json'},
      body: JSON.stringify({decision})
    });
  }
  return (
    <tr>
      <td>{task.payload.complaintId}</td>
      <td>{task.aiResult.severity}</td>
      <td>
        <button onClick={()=>action('approve')}>👍</button>
        <button onClick={()=>action('edit')}>✏️</button>
        <button onClick={()=>action('deny')}>👎</button>
      </td>
    </tr>
  );
}
```

Explanation  
1. Officer sees the AI result.  
2. One click POSTs an override back to HMS-ACT.  
3. UI is only glue—no business logic here.

### 4.3  Record the Decision (Python ≤19 lines)

```python
# act/routes.py
@app.post("/tasks/<id>/override")
def override(id):
    body = request.json
    store.update_task(id, status="OVERRIDDEN",
                           by=request.user,
                           decision=body["decision"])
    audit.log("override", task=id, user=request.user)
    friction.bump(request.user, id)       # update counter
    return {"status":"ok"}
```

*Beginners*:  
• `audit.log` writes to the same CSV ledger we used in Chapter 11.  
• `friction.bump` counts how often this officer overrides this model.

---

## 5. Step-By-Step: What Happens Under the Hood

```mermaid
sequenceDiagram
  participant AI  as AI Model
  participant ACT as HMS-ACT
  participant Q   as HITL Queue
  participant OFF as Loan Officer
  participant AUD as Audit Log

  AI-->>ACT: result = "Approve"
  ACT->>Q: create queue item
  OFF->>Q: open item
  OFF->>ACT: POST /override ("Deny")
  ACT->>AUD: write override stamp
  ACT-->>AI: feedback ("High friction")
```

1. AI result **stops** in the queue.  
2. Officer overrides.  
3. Audit trail gets both the AI suggestion and human decision.  
4. High friction sends a signal back to AI training (next chapter).

---

## 6. Under-the-Hood Code Peeks

### 6.1  Queue Table (SQL ≤8 lines)

```sql
CREATE TABLE hitl_queue (
  id       UUID PRIMARY KEY,
  task_id  UUID,
  ai_json  JSONB,
  status   TEXT,    -- PENDING / RESOLVED
  created  TIMESTAMPTZ DEFAULT now()
);
```

Every AI suggestion waiting for review is exactly **one row**.

### 6.2  Friction Counter (Go ≤12 lines)

```go
// friction/store.go
func Bump(user, model string) {
  key := fmt.Sprintf("%s:%s", user, model)      // officer:model
  redis.Incr(key)
  if redis.Get(key) > 10 {                      // threshold
     notifyPerformanceTeam(user, model)
  }
}
```

When overrides exceed 10 in 30 days, HITL triggers a **performance review**.

### 6.3  Override API Guard (Python ≤14 lines)

```python
def can_override(user, task):
    roles = get_roles(user)
    if "Supervisor" in roles: return True
    return task.owner == user
```

Simple rule: supervisors can override anything; others only their own tasks.

---

## 7. Common Pitfalls & Quick Fixes

| Symptom | Cause | Quick Fix |
|---------|-------|-----------|
| Queue is empty but AI says it finished | `review: human` missing | Add the field and redeploy workflow |
| Officers see `403 Forbidden` | Wrong role mapping | Ensure `Supervisor` or `Reviewer` role exists in HMS-GOV |
| Friction never triggers | Redis key TTL too short | Set key expiry to 30 days in `Bump()` |

---

## 8. Hands-On Exercise (10 min)

1. `git clone https://github.com/hms-samples/hitl-demo && cd hitl-demo`  
2. `docker-compose up` – starts ACT, queue DB, officer UI.  
3. Visit `http://localhost:8081` – AI suggestions appear.  
4. Override 12 times → watch console log: “⚠️  Friction threshold breached.”  
5. Open `audit.csv` – each override is logged.

---

## 9. Recap & What’s Next

You learned how **HITL Oversight**:

• Shows AI suggestions in a **Decision Queue**.  
• Gives humans a one-click **Override Button**.  
• Logs every action with an **Audit Stamp**.  
• Tracks **Friction** to spot weak models *or* overly strict officers.  

In the next chapter we’ll see how those override logs feed training data back into the system using the **Model Context Protocol (MCP)**.  
Continue to [Model Context Protocol (HMS-MCP)](13_model_context_protocol__hms_mcp__.md).

---

Generated by [HardisonCo [NARA-DOC]](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)