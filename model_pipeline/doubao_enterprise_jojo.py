import json

from loguru import logger
# from model_pipeline.model.prompt_voc_batch import agent_voc,sample_messages_agent_voc
# from model_pipeline.model.prompt_service_action_batch import agent_puke,agent_fuwudongzuo,agent_xueqinggoutong,sample_messages_agent_xueqinggoutong,sample_messages_agent_fuwudongzuo,sample_messages_agent_puke
# from model_pipeline.model.prompt_gkyy_v3_batch import agent_price,agent_intention,agent_course_effect,agent_course_consult,sample_messages_agent_price,sample_messages_agent_intention,sample_messages_agent_course_consult,sample_messages_agent_course_effect
# from model_pipeline.model.prompt_yyxc import agent_yyxc,sample_messages_agent_yyxc
# from model_pipeline.model.prompt_quality_test_batch_v2 import agent_fuwuxiaoji,agent_dihuigongsi,agent_budangxingwei,agent_zhengchaoruma,agent_xujiaxuanchuan,agent_jiaolvyingxiao
# # from model_pipeline.model.prompt_quality_test_conv import agent_fwxj_conv,agent_bdxw_conv,agent_zcrm_conv,agent_dhgs_conv,agent_jlyx_conv,agent_xjxc_conv
# from model_pipeline.model.prompt_quality_test_conv_1220 import agent_fwxj_conv,agent_bdxw_conv,agent_zcrm_conv,agent_dhgs_conv,agent_jlyx_conv,agent_xjxc_conv
# # from model_pipeline.model.prompt_user_feedback_v5 import agent_user_feedback_positive,agent_user_feedback_positive_samples,agent_user_feedback_negative,agent_user_feedback_negative_samples
# from model_pipeline.model.prompt_uf_v5 import agent_user_feedback_positive,agent_user_feedback_positive_samples,agent_user_feedback_negative,agent_user_feedback_negative_samples
# from model_pipeline.model.prompt_agent_staff_visit_v3 import agent_staff_agent_label_k,agent_staff_agent_label_k_samples,invalid_sessions_reply as asv_invalid_sessions_reply
# from model_pipeline.model.prompt_jojo import agent_jojo_label,jojo_label_input,agent_jojo_label_merge,old_user_tag,new_user_tag,user_tag_structure
from model_pipeline.model.prompt_jojo import get_pe_agent_jojo_label,get_pe_agent_jojo_label_merge

from volcenginesdkarkruntime import Ark
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

    prompt = ''
    sample_messages = []
    input_message = ''

    # # 学情家访 v3
    # elif agent_id == 'asv':
    #     prompt = agent_staff_agent_label_k
    #     sample_messages = agent_staff_agent_label_k_samples
    #
    # elif agent_id == 'asv_invalid':
    #     # prompt = agent_staff_agent_label_k
    #     # sample_messages = agent_staff_agent_label_k_samples
    #     reply = asv_invalid_sessions_reply
    #     return {
    #         'input': input,
    #         'agent_id':agent_id,
    #         'reply': reply,
    #         'hit_sessions': hit_sessions,
    #         'cost': 0.,
    #         'succeed_record': 0.,
    #         'execution_time': 0.
    #     }

    if agent_id == 'jojo_label':
        input = str(input)
        prompt = get_pe_agent_jojo_label(input)
        input_message = '请按要求输出用户画像的json数据'

    elif agent_id == 'jojo_label_merge':
        if len(input) != 3:
            input = ('','','')
        prompt = get_pe_agent_jojo_label_merge(input)
        input_message = '请按要求输出最终的用户画像特征结构数据'


    else:
        logger.warning('no exact agent id.')
        logger.warning(agent_id)



    system_set = [{"role": "system", "content": prompt}]
    input_message = [{"role": "user", "content": input_message}]
    # messages = system_set + sample_messages + input_message
    messages = system_set + input_message
    # messages = system_set

    response = None
    try:

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.6
        )

        reply = response.choices[0].message.content

        input_price = 0.0008
        output_price = 0.002

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

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
        if response and response.status_code == 200:
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

    # input =  "家长：宝贝每天都很喜欢听读  \n\n"
    # result = get_result(input,agent_id='jojo_label')
    # print(result['reply'])
    # print(json.dumps(result,indent=4,ensure_ascii=False))


    input = (
        "{\"基础信息\": {\"年龄\": \"\", \"生日\": \"\", \"聊天风格\": \"\", \"语言技能\": \"\"}, \"兴趣偏好\": {\"学科\": \"\", \"运动\": \"\", \"饮食偏好\": \"\", \"饮食禁忌\": \"\", \"社交\": \"\", \"游玩\": \"\", \"音乐\": \"\", \"虚拟IP\": \"\", \"人物\": \"\", \"文学作品\": \"\", \"艺术\": \"\", \"影视\": \"\", \"旅游\": \"\", \"萌宠\": \"\", \"电子产品\": \"\"}}",
        "{\n    \"基础信息\": {\n        \"昵称\": \"\",\n        \"年龄\": \"\",\n        \"生日\": \"\",\n        \"聊天风格\": \"直白\",\n        \"语言技能\": \"\"\n    },\n    \"兴趣偏好\": {\n        \"学科\": \"\",\n        \"运动\": \"\",\n        \"饮食偏好\": \"蛋炒饭,加咖喱的蛋炒饭\",\n        \"饮食禁忌\": \"\",\n        \"社交\": \"\",\n        \"游玩\": \"\",\n        \"音乐\": \"\",\n        \"虚拟IP\": \"\",\n        \"人物\": \"\",\n        \"文学作品\": \"\",\n        \"艺术\": \"\",\n        \"影视\": \"\",\n        \"旅游\": \"\",\n        \"动物\": \"\",\n        \"电子产品\": \"\",\n        \"服装饰品\": \"\"\n    }\n}",
        "\n    {\n        \"基础信息\": {\n            \"昵称\": \"\",\n            \"年龄\": \"\",\n            \"生日\": \"\",\n            \"聊天风格\": \"\",\n            \"语言技能\": \"\"\n        },\n        \"兴趣偏好\": {\n            \"学科\": \"\",\n            \"运动\": \"\",\n            \"饮食偏好\": \"\",\n            \"饮食禁忌\": \"\",\n            \"社交\": \"\",\n            \"游玩\": \"\",\n            \"音乐\": \"\",\n            \"虚拟IP\": \"\",\n            \"人物\": \"\",\n            \"文学作品\": \"\",\n            \"艺术\": \"\",\n            \"影视\": \"\",\n            \"旅游\": \"\",\n            \"动物\": \"\",\n            \"电子产品\": \"\",\n            \"服装饰品\": \"\"\n        }\n    }\n    "
    )
    result = get_result(input,agent_id='jojo_label_merge')
    print(result['reply'])
    print(json.dumps(result,indent=4,ensure_ascii=False))
