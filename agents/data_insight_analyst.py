from openai import OpenAI
import json
from typing import Dict, Any

class DataInsightAnalyst:
    def __init__(self, openai_api_key: str):
        if not openai_api_key:
            raise ValueError("API key not found in environment variables.")
        # 注意：使用您指定的SiliconFlow接入点
        self.openai_client = OpenAI(base_url='https://api.siliconflow.cn/v1', api_key=openai_api_key)
        print("数据洞察师已初始化，并被赋予'批判者'角色。")

    def run_critique(self, education_report: dict, industry_report: dict) -> Dict[str, Any]:
        """
        以"批判者"的身份，对教育和行业分析师的报告提出质疑和问题。
        注意：这个方法是为了适配新的"虚拟圆桌会议"范式。
        """
        major_name = education_report.get("major_name", "N/A")
        job_title = industry_report.get("job_title", "N/A")
        print(f"批判者开始审查 {major_name} 和 {job_title} 的分析报告...")

        education_skills = education_report.get("required_skills", [])
        industry_skills = industry_report.get("required_skills", [])
        
        # 如果上游数据不完整，无法进行有意义的批判
        if not education_skills or not industry_skills:
            return { "critique_summary": "上游报告信息不足，无法进行有效批判。", "questions_for_next_round": [] }

        try:
            system_prompt = """
            You are a sharp, critical, and detail-oriented data scientist. Your role is not to find agreements, but to challenge assumptions and identify weaknesses in the analysis provided by an education expert and an industry expert.

            You are given two analysis reports: one on a university major (`education_report`) and one on a job role (`industry_report`). Your task is to:
            
            1.  **Identify Discrepancies and Gaps**: Scrutinize both skill lists. Where are the mismatches? What crucial industry skills are completely missing from the education side?
            
            2.  **Challenge Vague Terms**: If the education report lists a generic skill like "programming", but the industry demands specific languages like "Python" and "Go", you must point this out.
            
            3.  **Question Both Sides**: Don't just focus on education shortcomings. Also challenge:
                - Are the industry requirements realistic or outdated?
                - Are there emerging skills that industry hasn't recognized yet?
                - Do market trends align with current job requirements?
                - Are career growth paths accurately represented?
            
            4.  **Formulate Balanced Questions**: Generate specific, actionable questions that will help BOTH the education expert AND industry expert provide better analysis in the next round. Balance questions between:
                - Education curriculum gaps and improvements needed
                - Industry market trends and evolving requirements
                - Skills alignment and practical application

            Your questions should drive both experts to provide deeper, more concrete information.

            Respond ONLY with a valid JSON object in the following format:
            {
                "critique_summary": "A brief summary of the main weaknesses found in BOTH education and industry analyses.",
                "questions_for_next_round": ["Question 1 (for education)?", "Question 2 (for industry)?", "Question 3 (for both)?"]
            }
            """
            
            user_prompt = f"""
            Here are the reports for your critique:
            Education Report: {json.dumps(education_report, ensure_ascii=False)}
            Industry Report: {json.dumps(industry_report, ensure_ascii=False)}
            Please provide your critique and questions.
            """

            print("--> 正在连接DeepSeek API进行批判性分析...")
            print("--> 预计需要30-45秒，正在进行深度质疑...")
            response = self.openai_client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            print("--> 正在解析批判分析结果...")
            # 安全的JSON解析
            response_content = response.choices[0].message.content
            print(f"--> 收到批判响应内容: {response_content[:200]}...")  # 打印前200字符用于调试
            
            try:
                critique_result = json.loads(response_content)
                
                # 验证返回的数据结构
                if not isinstance(critique_result, dict):
                    raise ValueError(f"期望字典格式，但收到: {type(critique_result)}")
                
                # 确保必要字段存在
                if "critique_summary" not in critique_result:
                    critique_result["critique_summary"] = "批判分析出现问题"
                if "questions_for_next_round" not in critique_result:
                    critique_result["questions_for_next_round"] = []
                elif not isinstance(critique_result["questions_for_next_round"], list):
                    critique_result["questions_for_next_round"] = []
                
                print("--> 批判性分析完成。")
                
            except json.JSONDecodeError as e:
                print(f"--> 批判JSON解析失败: {e}")
                # 返回默认结构
                critique_result = {
                    "critique_summary": "JSON解析失败，无法进行有效批判",
                    "questions_for_next_round": []
                }
            
            return critique_result

        except Exception as e:
            print(f"--> 批判者在执行中出错: {e}")
            return { "error": "Failed during critique analysis.", "details": str(e) }

    def run(self, education_report: dict, industry_report: dict) -> dict:
        """
        使用DeepSeek模型对专业和行业的技能进行语义匹配分析
        现在具有更强的错误处理能力
        """
        print("数据洞察师开始进行最终量化分析...")
        
        # 使用改进的量化分析方法，具有更好的错误处理能力
        try:
            analysis_result = self.final_quantitative_analysis(education_report, industry_report)
            
            # 转换为兼容的输出格式
            return {
                "match_score_percent": analysis_result.get("matching_score", 0),
                "matching_level": analysis_result.get("matching_level", "需要提升"),
                "common_skills_semantic": {
                    "core_matches": analysis_result["analysis_summary"].get("core_skills_matched", []),
                    "related_matches": analysis_result["analysis_summary"].get("related_skills_matched", [])
                },
                "skill_gaps": analysis_result["analysis_summary"].get("skill_gaps", []),
                "education_highlights": education_report.get("core_courses", []),
                "industry_highlights": industry_report.get("responsibilities", []),
                "summary": f"匹配度分析完成：{analysis_result.get('matching_score', 0):.1f}分 ({analysis_result.get('matching_level', '需要提升')})"
            }
            
        except Exception as e:
            print(f"--> 量化分析过程出错: {e}")
            
            # 即使出错也返回基本的分析结果
            return {
                "match_score_percent": 45.0,  # 给一个中等分数
                "matching_level": "基础匹配",
                "common_skills_semantic": {
                    "core_matches": ["基础技能匹配"],
                    "related_matches": ["相关技能匹配"]
                },
                "skill_gaps": ["分析过程出现问题，建议手动评估"],
                "education_highlights": education_report.get("core_courses", ["基础课程"]),
                "industry_highlights": industry_report.get("responsibilities", ["基础职责"]),
                "summary": "由于技术问题，提供基础匹配度评估：45.0分 (基础匹配)",
                "error_note": f"分析过程遇到技术问题: {str(e)}"
            }

    def final_quantitative_analysis(self, education_report, industry_report):
        print("正在对 {} 和 {} 进行语义技能匹配分析...".format(
            education_report.get('major_name', '未知专业'),
            industry_report.get('job_title', '未知岗位')
        ))

        # 获取数据，处理可能的错误情况
        if 'error' in education_report:
            education_skills = ["通用编程能力", "逻辑思维", "问题解决能力"]
            education_courses = ["基础课程", "专业核心课程"]
            print(f"--> 教育分析有错误，使用默认技能列表")
        else:
            education_skills = education_report.get('required_skills', [])
            education_courses = education_report.get('core_courses', [])

        if 'error' in industry_report:
            industry_skills = ["编程开发", "技术研究", "团队协作"]
            print(f"--> 行业分析有错误，使用默认需求列表")
        else:
            industry_skills = industry_report.get('required_skills', [])

        # 确保数据不为空
        if not education_skills:
            education_skills = ["基础专业技能", "理论知识", "学习能力"]
        if not industry_skills:
            industry_skills = ["专业技能", "实践能力", "工作经验"]

        # 构建分析Prompt
        system_prompt = """
        You are an expert career counselor performing skills matching analysis. 

        Given education skills and industry requirements, identify:
        1. **core_skills_matched**: Direct skill matches (high relevance)
        2. **related_skills_matched**: Indirect/transferable skills (medium relevance)  
        3. **skill_gaps**: Skills required by industry but missing from education

        Be generous in finding connections and transferable skills. Consider that:
        - General programming can match specific languages
        - Theoretical knowledge can transfer to practical applications
        - Academic projects demonstrate real-world capabilities

        Respond ONLY with a valid JSON object:
        {
            "core_skills_matched": ["skill1", "skill2"],
            "related_skills_matched": ["skill3", "skill4"], 
            "skill_gaps": ["gap1", "gap2"]
        }
        
        CRITICAL: All fields must be arrays. Be optimistic in matching.
        """

        user_prompt = f"""
        教育技能 (来自专业培养): {education_skills}
        行业需求 (来自岗位要求): {industry_skills}
        核心课程参考: {education_courses}
        
        请基于以上信息进行技能匹配分析。注意要积极寻找可转移的技能连接。
        """

        try:
            print("--> 正在连接DeepSeek API进行加权语义分析...")
            print("--> 预计需要45-60秒，正在进行技能匹配分析...")
            response = self.openai_client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            print("--> 正在解析量化分析结果...")
            # 安全的JSON解析
            response_content = response.choices[0].message.content
            print(f"--> 收到量化分析响应内容: {response_content[:200]}...")  # 打印前200字符用于调试
            
            try:
                analysis = json.loads(response_content)
                
                # 验证返回的数据结构
                if not isinstance(analysis, dict):
                    raise ValueError(f"期望字典格式，但收到: {type(analysis)}")
                
                # 确保必要字段存在，如果不存在则设置默认值
                required_fields = {
                    "core_skills_matched": [],
                    "related_skills_matched": [],
                    "skill_gaps": []
                }
                
                for field, default_value in required_fields.items():
                    if field not in analysis:
                        analysis[field] = default_value
                    elif not isinstance(analysis[field], list):
                        analysis[field] = default_value
                
                print("--> 加权语义分析完成。")
                
            except json.JSONDecodeError as e:
                print(f"--> 量化分析JSON解析失败: {e}")
                # 执行简单的关键词匹配作为备用
                analysis = self._simple_keyword_matching(education_skills, industry_skills)
                
        except Exception as e:
            print(f"--> DeepSeek API调用失败: {e}")
            # 执行简单的关键词匹配作为备用
            analysis = self._simple_keyword_matching(education_skills, industry_skills)

        # --- 全新的加权计分逻辑 ---
        core_matches = len(analysis.get("core_skills_matched", []))
        related_matches = len(analysis.get("related_skills_matched", []))
        gaps = len(analysis.get("skill_gaps", []))
        total_industry_skills = len(industry_skills)

        # 确保分母不为0
        if total_industry_skills == 0:
            total_industry_skills = 1

        # 调试信息
        print(f"--> 计分详情:")
        print(f"    核心匹配数量: {core_matches}")
        print(f"    相关匹配数量: {related_matches}")
        print(f"    技能差距数量: {gaps}")
        print(f"    行业总技能数量: {total_industry_skills}")
        print(f"    教育技能数量: {len(education_skills)}")

        # 优化的计分逻辑：更加公平和合理
        # 基础分数：基于实际匹配情况
        total_matches = core_matches + related_matches
        coverage_rate = total_matches / total_industry_skills if total_industry_skills > 0 else 0
        
        # 加权评分：核心技能更重要
        weighted_score = (core_matches * 4 + related_matches * 2) / max(total_matches, 1) if total_matches > 0 else 0
        
        # 综合评分 = 覆盖率 * 加权评分 * 100
        base_score = coverage_rate * weighted_score * 100
        
        # 技能差距的合理惩罚：不应该过度惩罚
        if total_industry_skills > 0:
            gap_penalty_rate = gaps / total_industry_skills
            gap_penalty = min(gap_penalty_rate * 30, 25)  # 最多扣25分
        else:
            gap_penalty = 0
        
        # 最终分数
        final_score = max(base_score - gap_penalty, 0)
        
        # 如果有匹配技能，最低给30分；如果有很多匹配，应该给更高分
        if total_matches > 0:
            # 根据匹配数量给出最低保障分数
            min_score = min(30 + total_matches * 5, 70)
            final_score = max(final_score, min_score)

        print(f"    覆盖率: {coverage_rate:.2f}")
        print(f"    加权评分: {weighted_score:.2f}")
        print(f"    基础分数: {base_score:.2f}")
        print(f"    差距惩罚: {gap_penalty:.2f}")
        print(f"    最终分数: {final_score:.2f}")

        # 匹配度等级
        if final_score >= 85:
            match_level = "极高匹配"
        elif final_score >= 70:
            match_level = "高度匹配" 
        elif final_score >= 55:
            match_level = "中等匹配"
        elif final_score >= 40:
            match_level = "基础匹配"
        else:
            match_level = "需要提升"

        print(f"--> 匹配分析完成: {final_score:.1f}分 ({match_level})")

        return {
            "analysis_summary": analysis,
            "matching_score": round(final_score, 1),
            "matching_level": match_level,
            "core_skills_count": core_matches,
            "related_skills_count": related_matches,
            "skill_gaps_count": gaps,
            "debug_info": {
                "education_skills_count": len(education_skills),
                "industry_skills_count": total_industry_skills,
                "coverage_rate": round(coverage_rate, 3),
                "base_score": round(base_score, 2),
                "gap_penalty": round(gap_penalty, 2)
            }
        }

    def _simple_keyword_matching(self, education_skills, industry_skills):
        """简单的关键词匹配作为备用策略"""
        print("--> 使用简单关键词匹配作为备用策略...")
        
        core_matches = []
        related_matches = []
        skill_gaps = []
        
        # 转换为小写进行匹配
        edu_skills_lower = [skill.lower() for skill in education_skills]
        
        for industry_skill in industry_skills:
            industry_lower = industry_skill.lower()
            matched = False
            
            # 检查直接匹配
            for edu_skill in education_skills:
                edu_lower = edu_skill.lower()
                if industry_lower in edu_lower or edu_lower in industry_lower:
                    core_matches.append(f"{edu_skill} → {industry_skill}")
                    matched = True
                    break
            
            # 如果没有直接匹配，检查相关关键词
            if not matched:
                related_keywords = {
                    'programming': ['编程', 'code', 'development', '开发'],
                    'algorithm': ['算法', 'logic', '逻辑'],
                    'database': ['数据库', 'data', '数据'],
                    'machine learning': ['机器学习', 'ai', '人工智能'],
                    'python': ['编程', 'programming'],
                    'java': ['编程', 'programming'],
                    'analysis': ['分析', 'analytical', '分析能力']
                }
                
                for keyword, synonyms in related_keywords.items():
                    if keyword in industry_lower:
                        for synonym in synonyms:
                            for edu_skill in education_skills:
                                if synonym in edu_skill.lower():
                                    related_matches.append(f"{edu_skill} ≈ {industry_skill}")
                                    matched = True
                                    break
                        if matched:
                            break
            
            # 如果仍然没有匹配，加入技能差距
            if not matched:
                skill_gaps.append(industry_skill)
        
        return {
            "core_skills_matched": core_matches,
            "related_skills_matched": related_matches,
            "skill_gaps": skill_gaps
        }
