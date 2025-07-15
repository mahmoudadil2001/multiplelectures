import streamlit as st
import importlib

def orders_o():
    # إعداد قائمة المحاضرات تلقائيًا من 1 إلى 15
    lectures = [f"Lecture {i}" for i in range(1, 16)]

    lecture = st.selectbox("اختر المحاضرة", lectures)

    # استخراج رقم المحاضرة من النص "Lecture X"
    lecture_num = int(lecture.split()[1])
    module_name = f"mcqs{lecture_num}"

    try:
        questions_module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        st.error(f"ملف الأسئلة للمحاضرة {lecture} غير موجود!")
        return

    question_prefix = f"Q{lecture_num}"

    questions = questions_module.questions

    # إعادة تهيئة session_state عند تغيير عدد الأسئلة أو المحاضرة
    if ("questions_count" not in st.session_state) or \
       (st.session_state.questions_count != len(questions)) or \
       (st.session_state.get("current_lecture", None) != lecture):

        st.session_state.questions_count = len(questions)
        st.session_state.current_question = 0
        st.session_state.user_answers = [None] * len(questions)
        st.session_state.answer_shown = [False] * len(questions)
        st.session_state.quiz_completed = False
        st.session_state.current_lecture = lecture

    def normalize_answer(q):
        answer = q.get("answer") or q.get("correct_answer")
        options = q["options"]

        if isinstance(answer, int) and 0 <= answer < len(options):
            return options[answer]

        if isinstance(answer, str):
            answer_clean = answer.strip().upper()
            if answer_clean in ["A", "B", "C", "D"]:
                idx = ord(answer_clean) - ord("A")
                if 0 <= idx < len(options):
                    return options[idx]
            if answer in options:
                return answer

        return None

    with st.sidebar:
        st.markdown("""
        <div style="display:flex; align-items:center; justify-content:space-between;">
          <h3>🧭 الأسئلة وإجاباتها</h3>
          <a href="https://t.me/IO_620" target="_blank"
             style="background:#0088cc; border-radius:50%; width:40px; height:40px; display:flex; align-items:center; justify-content:center; text-decoration:none;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" alt="Telegram" style="width:24px; height:24px;">
          </a>
        </div>
        """, unsafe_allow_html=True)

        for i in range(len(questions)):
            correct_text = normalize_answer(questions[i])
            user_ans = st.session_state.user_answers[i]
            if user_ans is None:
                status = "⬜"
            elif user_ans == correct_text:
                status = "✅"
            else:
                status = "❌"

            if st.button(f"{status} Question {i+1}", key=f"nav_{i}"):
                st.session_state.current_question = i

    def show_question(index):
        q = questions[index]
        correct_text = normalize_answer(q)

        st.markdown(f"### {question_prefix}/{index + 1}: {q['question']}")

        default_idx = 0
        if st.session_state.user_answers[index] in q["options"]:
            default_idx = q["options"].index(st.session_state.user_answers[index])

        selected_answer = st.radio(
            "",
            q["options"],
            index=default_idx,
            key=f"radio_{index}"
        )

        if not st.session_state.answer_shown[index]:
            if st.button("أجب", key=f"submit_{index}"):
                st.session_state.user_answers[index] = selected_answer
                st.session_state.answer_shown[index] = True
                st.rerun()
        else:
            user_ans = st.session_state.user_answers[index]
            if user_ans == correct_text:
                st.success("✅ إجابة صحيحة")
            else:
                st.error(f"❌ الإجابة الصحيحة: {correct_text}")

            if st.button("السؤال التالي", key=f"next_{index}"):
                if index + 1 < len(questions):
                    st.session_state.current_question += 1
                else:
                    st.session_state.quiz_completed = True
                st.rerun()

    if not st.session_state.quiz_completed:
        show_question(st.session_state.current_question)
    else:
        st.header("🎉 تم الانتهاء من الاختبار!")
        correct = 0
        for i, q in enumerate(questions):
            correct_text = normalize_answer(q)
            user = st.session_state.user_answers[i]
            if user == correct_text:
                correct += 1
                st.write(f"Q{i+1}: ✅ صحيحة")
            else:
                st.write(f"Q{i+1}: ❌ خاطئة (إجابتك: {user}, الصحيحة: {correct_text})")
        st.success(f"أجبت إجابة صحيحة على {correct} من أصل {len(questions)}")

        if st.button("🔄 أعد الاختبار"):
            st.session_state.current_question = 0
            st.session_state.user_answers = [None] * len(questions)
            st.session_state.answer_shown = [False] * len(questions)
            st.session_state.quiz_completed = False
            st.rerun()
