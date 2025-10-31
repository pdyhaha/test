from loguru import logger
# from model_pipeline.model.prompt_voc_batch import agent_voc,sample_messages_agent_voc
from model_pipeline.model.prompt_voc_batch_sp162 import agent_voc,sample_messages_agent_voc
from model_pipeline.model.prompt_service_action_batch import agent_puke,agent_fuwudongzuo,agent_xueqinggoutong,sample_messages_agent_xueqinggoutong,sample_messages_agent_fuwudongzuo,sample_messages_agent_puke
# from model_pipeline.model.prompt_gkyy_v3_batch import agent_price,agent_intention,agent_course_effect,agent_course_consult,sample_messages_agent_price,sample_messages_agent_intention,sample_messages_agent_course_consult,sample_messages_agent_course_effect
from model_pipeline.model.prompt_gkyy_batch_sp162 import agent_price,agent_intention,agent_course_effect,agent_course_consult,sample_messages_agent_price,sample_messages_agent_intention,sample_messages_agent_course_consult,sample_messages_agent_course_effect
from model_pipeline.model.prompt_yyxc import agent_yyxc,sample_messages_agent_yyxc
from model_pipeline.model.prompt_quality_test_batch_v2 import agent_fuwuxiaoji,agent_dihuigongsi,agent_budangxingwei,agent_zhengchaoruma,agent_xujiaxuanchuan,agent_jiaolvyingxiao
# from model_pipeline.model.prompt_quality_test_conv import agent_fwxj_conv,agent_bdxw_conv,agent_zcrm_conv,agent_dhgs_conv,agent_jlyx_conv,agent_xjxc_conv
from model_pipeline.model.prompt_quality_test_conv_1220 import agent_fwxj_conv,agent_bdxw_conv,agent_zcrm_conv,agent_dhgs_conv,agent_jlyx_conv,agent_xjxc_conv
# from model_pipeline.model.prompt_user_feedback_v5 import agent_user_feedback_positive,agent_user_feedback_positive_samples,agent_user_feedback_negative,agent_user_feedback_negative_samples
from model_pipeline.model.prompt_uf_v5 import agent_user_feedback_positive,agent_user_feedback_positive_samples,agent_user_feedback_negative,agent_user_feedback_negative_samples
from model_pipeline.model.prompt_agent_staff_visit_v3 import agent_staff_agent_label_k,agent_staff_agent_label_k_samples,invalid_sessions_reply as asv_invalid_sessions_reply

from volcenginesdkarkruntime import Ark
from typing import List, Dict, Any, Union
import time


# 安装时如果使用conda创建的py环境会因为包文件名称过长出现BUG
# 解决方法https://github.com/volcengine/volcengine-python-sdk/issues/5

client = Ark(api_key='e88e554a-454c-4454-bff5-e08e86ff8f96')
# model = 'ep-20240730134105-2gwfm'
# model = 'ep-20240912105919-6x2q9'

# doubao 1.5pro
model = 'ep-20250702102639-vzf49'





def get_result(input,agent_id,hit_sessions = []):
    start_time = time.time()
    input = str(input)

    prompt = ''
    sample_messages = []

    # voc
    if agent_id == 'voc':
        prompt = agent_voc
        sample_messages =sample_messages_agent_voc

    # 服务动作
    elif agent_id == 'xqgt':
        # 学情沟通点评
        prompt = agent_xueqinggoutong
        sample_messages = sample_messages_agent_xueqinggoutong
    elif agent_id == 'puke':
        # 铺课
        prompt = agent_puke
        sample_messages = sample_messages_agent_puke
    elif agent_id == 'fwdz':
        # 其他服务动作
        prompt = agent_fuwudongzuo
        sample_messages = sample_messages_agent_fuwudongzuo


    # 购课异议识别
    elif agent_id == 'prc':
        prompt = agent_price
        sample_messages  = sample_messages_agent_price
    elif agent_id == 'csef':
        prompt = agent_course_effect
        sample_messages  = sample_messages_agent_course_effect
    # elif agent_name == 'course_consult':
    elif agent_id == 'cscs':
        prompt = agent_course_consult
        sample_messages  = sample_messages_agent_course_consult
    # elif agent_name == 'intention':
    elif agent_id == 'itnt':
        prompt = agent_intention
        sample_messages  = sample_messages_agent_intention

    # 异议消除
    elif agent_id == 'hesitation_dissent':
        prompt = agent_yyxc
        sample_messages  = sample_messages_agent_yyxc


    # 用户反馈v2

    elif agent_id == 'ufp':
        prompt = agent_user_feedback_positive
        sample_messages = agent_user_feedback_positive_samples
    elif agent_id == 'ufn':
        prompt = agent_user_feedback_negative
        sample_messages = agent_user_feedback_negative_samples


    # 学情家访 v3
    elif agent_id == 'asv':
        prompt = agent_staff_agent_label_k
        sample_messages = agent_staff_agent_label_k_samples

    elif agent_id == 'asv_invalid':
        # prompt = agent_staff_agent_label_k
        # sample_messages = agent_staff_agent_label_k_samples
        reply = asv_invalid_sessions_reply
        return {
            'input': input,
            'agent_id':agent_id,
            'reply': reply,
            'hit_sessions': hit_sessions,
            'cost': 0.,
            'succeed_record': 0.,
            'execution_time': 0.
        }



    else:
        logger.warning('no exact agent id.')



    system_set = [{"role": "system", "content": prompt}]
    input_message = [{"role": "user", "content": input}]
    # 确保消息格式正确
    messages = system_set + sample_messages + input_message

    response = None
    try:

        response = client.chat.completions.create(
            model=model,
            messages=messages,  # type: ignore
            temperature=0.6,
            stream=False
        )

        reply = response.choices[0].message.content  # type: ignore

        input_price = 0.0008
        output_price = 0.002

        input_tokens = response.usage.prompt_tokens if response.usage else 0  # type: ignore
        output_tokens = response.usage.completion_tokens if response.usage else 0  # type: ignore

        cost = input_tokens / 1000 * input_price + output_tokens / 1000 * output_price

        return {
            'input': input,
            'agent_id':agent_id,
            'reply': reply,
            'hit_sessions': hit_sessions,
            'cost': round(cost,4),
            'succeed_record': 1,
            'execution_time': time.time() - start_time
        }

    except Exception as e:
        if response and hasattr(response, 'choices') and response.choices:  # type: ignore
            return {
                'input': input,
                'agent_id':agent_id,
                'reply': '',
                'hit_sessions':hit_sessions,
                'cost': 0.,
                'succeed_record': 1,
                'execution_time': time.time() - start_time
            }
        else:
            return {
                'input': input,
                'agent_id':agent_id,
                'reply': '',
                'hit_sessions': hit_sessions,
                'cost': 0.,
                'succeed_record': 0,
                'execution_time': time.time() - start_time
            }

if __name__ == "__main__":
#     input = """
#     老师：为了确保更好的学习体验，方便了解一下宝贝目前的英语基础吗？
#
# 家长：零基础
#
# 家长：齐齐一年级
#
# 老师：好的好的，琪琪妈妈，我这个已经备注了哈。咱们的课程的话是明天开课，全天都可以学，时间都是灵活安排的。咱们本次体育课呢，它也是针对于咱们临几个宝贝的。
#
# 老师：内容从基础的字母自然拼读到词汇再到句型结合，最终让宝贝达到整体的绘本阅读，从听说读写提升孩子全方位的英语能力
#
# 老师：宝贝家长，2分钟后我们群内班会开始了哟，您记得来群里看看[胜利]
#
#     """
    input =  "家长：宝贝每天都很喜欢听读  \n\n"
    result = get_result(input,agent_id='asv')
    print(result['reply'])

