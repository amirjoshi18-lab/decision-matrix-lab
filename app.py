import os
from flask import Flask, render_template, request, jsonify, make_response
from datetime import datetime

# --- FORCE EXPLICIT PATH FOR RENDER OSLOAD ---
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)
# ---------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_report', methods=['POST'])
def generate_report():
    data = request.json
    
    company_name = data.get('companyName', 'Target Startup Operations')
    team_members = data.get('teamMembers', 'Anonymous Researchers')
    solutions = data.get('solutions', [])
    criteria = data.get('criteria', [])
    chosen_index = int(data.get('chosenSolutionIndex', 0))
    chart_image = data.get('chartImage', '')
    
    if not solutions or chosen_index >= len(solutions):
        return jsonify({'error': 'Invalid matrix datasets received'}), 400
        
    chosen_solution = solutions[chosen_index]
    
    def normalize_weight(w_val):
        try:
            val = float(w_val)
            return val / 100.0 if val > 1.0 else val
        except (ValueError, TypeError):
            return 0.0

    sorted_criteria = sorted(criteria, key=lambda x: normalize_weight(x.get('weight', 0)), reverse=True)
    top_crit_1 = sorted_criteria[0]['name'] if len(sorted_criteria) > 0 else 'Core Metrics'
    top_crit_2 = sorted_criteria[1]['name'] if len(sorted_criteria) > 1 else 'Secondary Metrics'
    
    chosen_score_on_top = 0
    for c in criteria:
        if c['name'] == top_crit_1:
            chosen_score_on_top = c['scores'][chosen_index]
            break

    score_out_of_max = round(float(chosen_solution['totalScore']), 2)
    
    runner_up_name = "Alternative Options"
    runner_up_score = 0
    for idx, sol in enumerate(solutions):
        if idx != chosen_index and float(sol['totalScore']) > runner_up_score:
            runner_up_score = float(sol['totalScore'])
            runner_up_name = sol['name']
    
    runner_up_score = round(runner_up_score, 2)

    p1 = f"This document establishes the empirical engineering validation for selecting {chosen_solution['name']} " \
         f"as the primary communication and systems documentation layer for {company_name}. Prepared by lead researchers " \
         f"{team_members}, this technical recommendation summarizes an extensive architectural trade study. Based on a " \
         f"normalized objective calculation framework, {chosen_solution['name']} yielded a definitive performance index of " \
         f"{score_out_of_max} points, outclassing the closest baseline infrastructure alternative, {runner_up_name}, " \
         f"which stalled at {runner_up_score} points. Core tracking indicates this selection is primarily driven by " \
         f"superior stress tolerance in high-weight architectural demands—specifically {top_crit_1} and {top_crit_2}."

    p2 = f"The structural deployment justification of {chosen_solution['name']} is validated by isolating quantitative " \
         f"and qualitative indicators across the evaluation grid. The target solution achieved an elite benchmark score of " \
         f"{chosen_score_on_top}/100 in the critical system performance dimension of {top_crit_1}. This performance ensures immediate " \
         f"mitigation of transactional and scaling risk paths. While competing operational layers failed to support " \
         f"long-term data retention integrity without incurring extensive technical debt, the recommended asset stack provides a " \
         f"sustainable foundation. It successfully aligns deployment constraints with the client's current software development lifecycle (SDLC) goals."

    research_bullets = []
    for c in criteria:
        keywords = c.get('keywords', '').strip()
        if keywords:
            score_val = c['scores'][chosen_index]
            research_bullets.append(
                f"<div style='margin-bottom: 4px; font-family: sans-serif;'>"
                f"  <span style='color: #1e3a8a; font-weight: bold; font-size: 12px;'>■ Criterion Evaluation: {c['name']}</span> "
                f"  <span style='background-color: #e0f2fe; color: #0369a1; font-size: 10px; font-family: monospace; padding: 1px 5px; border-radius: 4px; margin-left: 6px; font-weight: bold;'>Score: {score_val}/100</span>"
                f"</div>"
                f"<div style='padding-left: 12px; color: #475569; font-style: italic; margin-bottom: 14px; border-left: 2px solid #cbd5e1; font-size: 11.5px;'>"
                f"  <strong>Student Notes & Observations:</strong> \"{keywords}\""
                f"</div>"
            )

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return jsonify({
        'paragraph1': p1,
        'paragraph2': p2,
        'bullets': research_bullets,
        'companyName': company_name,
        'teamMembers': team_members,
        'timestamp': timestamp,
        'solutions': solutions,
        'chosenIndex': chosen_index,
        'chartImage': chart_image
    })

@app.route('/download_html', methods=['POST'])
def download_html():
    report_html = request.form.get('htmlContent', '')
    
    printable_doc = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; margin: 40px; color: #1e293b; line-height: 1.6; font-size: 12px; }}
            h2 {{ color: #1e3a8a; border-bottom: 2px solid #cbd5e1; padding-bottom: 6px; font-size: 16px; font-weight: bold; margin-top: 25px; text-transform: uppercase; }}
            h3 {{ color: #2563eb; font-size: 13px; margin-top: 15px; text-transform: uppercase; font-family: monospace; }}
            h4 {{ color: #475569; font-size: 12px; margin-top: 5px; font-weight: normal; }}
            p {{ text-align: justify; margin-bottom: 12px; color: #334155; }}
            .chart-box {{ text-align: center; margin: 25px 0; background: #f8fafc; padding: 15px; border: 1px solid #e2e8f0; border-radius: 6px; }}
            .chart-box img {{ max-width: 100%; height: auto; display: inline-block; }}
            .meta {{ font-size: 9px; color: #64748b; font-family: monospace; display: block; margin-top: 35px; border-top: 1px solid #e2e8f0; padding-top: 8px; }}
            @media print {{
                .no-print {{ display: none !important; }}
                body {{ margin: 20px; }}
            }}
        </style>
    </head>
    <body>
        <div class="no-print" style="background:#f1f5f9; padding:10px; border-radius:6px; margin-bottom:20px; font-family:sans-serif; font-size:11px; color:#475569; display:flex; justify-content:space-between; items-center:center;">
            <span>💡 This file can be saved offline or printed directly using your browser's Print option.</span>
            <button onclick="window.print()" style="background:#2563eb; color:white; border:none; padding:4px 10px; border-radius:4px; font-weight:bold; cursor:pointer;">Print / Save as PDF</button>
        </div>
        {report_html}
    </body>
    </html>
    """
    
    response = make_response(printable_doc)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=Technical_Recommendation_Report.html'
    return response

if __name__ == '__main__':
    app.run(debug=True)    
    runner_up_name = "Alternative Options"
    runner_up_score = 0
    for idx, sol in enumerate(solutions):
        if idx != chosen_index and float(sol['totalScore']) > runner_up_score:
            runner_up_score = float(sol['totalScore'])
            runner_up_name = sol['name']
    
    runner_up_score = round(runner_up_score, 2)

    # Paragraph 1: Executive Infrastructure Summary
    p1 = f"This document establishes the empirical engineering validation for selecting {chosen_solution['name']} " \
         f"as the primary communication and systems documentation layer for {company_name}. Prepared by lead researchers " \
         f"{team_members}, this technical recommendation summarizes an extensive architectural trade study. Based on a " \
         f"normalized objective calculation framework, {chosen_solution['name']} yielded a definitive performance index of " \
         f"{score_out_of_max} points, outclassing the closest baseline infrastructure alternative, {runner_up_name}, " \
         f"which stalled at {runner_up_score} points. Core tracking indicates this selection is primarily driven by " \
         f"superior stress tolerance in high-weight architectural demands—specifically {top_crit_1} and {top_crit_2}."

    # Paragraph 2: Comprehensive Technical Justification & Statement Logic
    p2 = f"The structural deployment justification of {chosen_solution['name']} is validated by isolating quantitative " \
         f"and qualitative indicators across the evaluation grid. The target solution achieved an elite benchmark score of " \
         f"{chosen_score_on_top}/100 in the critical system performance dimension of {top_crit_1}. This performance ensures immediate " \
         f"mitigation of transactional and scaling risk paths. While competing operational layers failed to support " \
         f"long-term data retention integrity without incurring extensive technical debt, the recommended asset stack provides a " \
         f"sustainable foundation. It successfully aligns deployment constraints with the client's current software development lifecycle (SDLC) goals."

    # Formats a clean, logical breakdown instead of mixing grammar awkwardly
    research_bullets = []
    for c in criteria:
        keywords = c.get('keywords', '').strip()
        if keywords:
            score_val = c['scores'][chosen_index]
            research_bullets.append(
                f"<div style='margin-bottom: 4px; font-family: sans-serif;'>"
                f"  <span style='color: #1e3a8a; font-weight: bold; font-size: 12px;'>■ Criterion Evaluation: {c['name']}</span> "
                f"  <span style='background-color: #e0f2fe; color: #0369a1; font-size: 10px; font-family: monospace; padding: 1px 5px; border-radius: 4px; margin-left: 6px; font-weight: bold;'>Score: {score_val}/100</span>"
                f"</div>"
                f"<div style='padding-left: 12px; color: #475569; font-style: italic; margin-bottom: 14px; border-left: 2px solid #cbd5e1; font-size: 11.5px;'>"
                f"  <strong>Student Notes & Observations:</strong> \"{keywords}\""
                f"</div>"
            )

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return jsonify({
        'paragraph1': p1,
        'paragraph2': p2,
        'bullets': research_bullets,
        'companyName': company_name,
        'teamMembers': team_members,
        'timestamp': timestamp,
        'solutions': solutions,
        'chosenIndex': chosen_index,
        'chartImage': chart_image
    })

@app.route('/download_html', methods=['POST'])
def download_html():
    report_html = request.form.get('htmlContent', '')
    
    # Packaged standalone container document layout
    printable_doc = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; margin: 40px; color: #1e293b; line-height: 1.6; font-size: 12px; }}
            h2 {{ color: #1e3a8a; border-bottom: 2px solid #cbd5e1; padding-bottom: 6px; font-size: 16px; font-weight: bold; margin-top: 25px; text-transform: uppercase; }}
            h3 {{ color: #2563eb; font-size: 13px; margin-top: 15px; text-transform: uppercase; font-family: monospace; }}
            h4 {{ color: #475569; font-size: 12px; margin-top: 5px; font-weight: normal; }}
            p {{ text-align: justify; margin-bottom: 12px; color: #334155; }}
            .chart-box {{ text-align: center; margin: 25px 0; background: #f8fafc; padding: 15px; border: 1px solid #e2e8f0; border-radius: 6px; }}
            .chart-box img {{ max-width: 100%; height: auto; display: inline-block; }}
            .meta {{ font-size: 9px; color: #64748b; font-family: monospace; display: block; margin-top: 35px; border-top: 1px solid #e2e8f0; padding-top: 8px; }}
            @media print {{
                .no-print {{ display: none !important; }}
                body {{ margin: 20px; }}
            }}
        </style>
    </head>
    <body>
        <div class="no-print" style="background:#f1f5f9; padding:10px; border-radius:6px; margin-bottom:20px; font-family:sans-serif; font-size:11px; color:#475569; display:flex; justify-content:space-between; items-center:center;">
            <span>💡 This file can be saved offline or printed directly using your browser's Print option.</span>
            <button onclick="window.print()" style="background:#2563eb; color:white; border:none; padding:4px 10px; border-radius:4px; font-weight:bold; cursor:pointer;">Print / Save as PDF</button>
        </div>
        {report_html}
    </body>
    </html>
    """
    
    response = make_response(printable_doc)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=Technical_Recommendation_Report.html'
    return response

if __name__ == '__main__':
    app.run(debug=True)
