"""
对话状态管理器 - 管理多轮对话的上下文和状态

核心功能：
1. 会话管理 - 创建、维护和清理对话会话
2. 上下文继承 - 支持跨查询的上下文传递
3. 意图追踪 - 跟踪用户意图的变化
4. 实体记忆 - 记住已提及的实体
5. 历史记录 - 保存对话历史用于回溯

作者: AI Assistant
日期: 2026-03-18
"""

import json
import re
import uuid
import time
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import threading
import logging

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """意图类型"""
    QUERY = "query"             # 数据查询
    ANALYSIS = "analysis"       # 分析请求
    COMPARISON = "comparison"   # 对比请求
    DRILL_DOWN = "drill_down"   # 下钻查询
    CLARIFICATION = "clarification"  # 澄清请求
    FOLLOW_UP = "follow_up"     # 跟进问题
    NEW_TOPIC = "new_topic"     # 新话题


@dataclass
class EntityMemory:
    """实体记忆"""
    entity_type: str
    value: Any
    confidence: float
    first_mentioned: datetime
    last_mentioned: datetime
    mention_count: int = 1


@dataclass
class QueryContext:
    """查询上下文"""
    query_id: str
    timestamp: datetime
    original_query: str
    intent: IntentType
    entities: List[Dict[str, Any]]
    sql: Optional[str] = None
    results_summary: Optional[str] = None
    filter_conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DialogueState:
    """对话状态"""
    session_id: str
    created_at: datetime
    last_activity: datetime
    current_intent: Optional[IntentType] = None
    entity_memory: Dict[str, EntityMemory] = field(default_factory=dict)
    query_history: List[QueryContext] = field(default_factory=list)
    current_filters: Dict[str, Any] = field(default_factory=dict)
    pending_clarification: Optional[str] = None
    context_variables: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'current_intent': self.current_intent.value if self.current_intent else None,
            'entity_memory': {
                k: {
                    'entity_type': v.entity_type,
                    'value': v.value,
                    'confidence': v.confidence,
                    'first_mentioned': v.first_mentioned.isoformat(),
                    'last_mentioned': v.last_mentioned.isoformat(),
                    'mention_count': v.mention_count,
                }
                for k, v in self.entity_memory.items()
            },
            'query_history': [
                {
                    'query_id': q.query_id,
                    'timestamp': q.timestamp.isoformat(),
                    'original_query': q.original_query,
                    'intent': q.intent.value if q.intent else None,
                    'entities': q.entities,
                    'sql': q.sql,
                    'results_summary': q.results_summary,
                    'filter_conditions': q.filter_conditions,
                }
                for q in self.query_history[-10:]  # 只保留最近10条
            ],
            'current_filters': self.current_filters,
            'pending_clarification': self.pending_clarification,
            'context_variables': self.context_variables,
        }


class DialogueStateManager:
    """
    对话状态管理器

    使用示例:
        manager = DialogueStateManager()

        # 创建新会话
        session = manager.create_session()

        # 处理查询
        manager.add_query(session.session_id, "昨天音频模块的缺陷")

        # 获取上下文
        context = manager.get_context(session.session_id)

        # 跟进查询（自动继承上下文）
        manager.add_query(session.session_id, "其中Critical级别的有多少")
    """

    # 会话超时时间（分钟）
    SESSION_TIMEOUT = 30

    # 最大历史记录数
    MAX_HISTORY = 20

    def __init__(self):
        self.sessions: Dict[str, DialogueState] = {}
        self._lock = threading.Lock()
        self._cleanup_interval = 300  # 5分钟清理一次
        self._last_cleanup = time.time()

    def create_session(self) -> DialogueState:
        """
        创建新会话

        Returns:
            新创建的对话状态
        """
        session_id = str(uuid.uuid4())
        now = datetime.now()

        state = DialogueState(
            session_id=session_id,
            created_at=now,
            last_activity=now
        )

        with self._lock:
            self.sessions[session_id] = state

        logger.info(f"Created new session: {session_id}")
        return state

    def get_session(self, session_id: str) -> Optional[DialogueState]:
        """
        获取会话状态

        Args:
            session_id: 会话ID

        Returns:
            对话状态或None
        """
        self._cleanup_if_needed()

        with self._lock:
            state = self.sessions.get(session_id)
            if state:
                state.last_activity = datetime.now()
            return state

    def close_session(self, session_id: str):
        """
        关闭会话

        Args:
            session_id: 会话ID
        """
        with self._lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                logger.info(f"Closed session: {session_id}")

    def add_query(self, session_id: str, query: str,
                  intent: Optional[IntentType] = None,
                  entities: Optional[List[Dict]] = None,
                  sql: Optional[str] = None,
                  results_summary: Optional[str] = None) -> QueryContext:
        """
        添加查询到会话

        Args:
            session_id: 会话ID
            query: 原始查询
            intent: 查询意图
            entities: 提取的实体
            sql: 生成的SQL
            results_summary: 结果摘要

        Returns:
            查询上下文
        """
        state = self.get_session(session_id)
        if not state:
            logger.warning(f"Session not found: {session_id}")
            state = self.create_session()

        # 分析意图（如果没有提供）
        if intent is None:
            intent = self._analyze_intent(query, state)

        # 合并实体（继承上下文）
        merged_entities = self._merge_entities(entities or [], state)

        # 创建查询上下文
        context = QueryContext(
            query_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            original_query=query,
            intent=intent,
            entities=merged_entities,
            sql=sql,
            results_summary=results_summary,
            filter_conditions=self._extract_filters(entities or [])
        )

        with self._lock:
            # 添加到历史
            state.query_history.append(context)

            # 限制历史长度
            if len(state.query_history) > self.MAX_HISTORY:
                state.query_history = state.query_history[-self.MAX_HISTORY:]

            # 更新实体记忆
            self._update_entity_memory(state, entities or [])

            # 更新当前意图
            state.current_intent = intent

            # 更新过滤器
            state.current_filters.update(context.filter_conditions)

            # 更新活动时间
            state.last_activity = datetime.now()

        logger.info(f"Added query to session {session_id}: {query[:50]}...")
        return context

    def get_context(self, session_id: str) -> Dict[str, Any]:
        """
        获取当前上下文信息

        Args:
            session_id: 会话ID

        Returns:
            上下文信息字典
        """
        state = self.get_session(session_id)
        if not state:
            return {}

        # 获取最近查询
        recent_queries = state.query_history[-3:] if state.query_history else []

        # 获取活跃实体（最近提及的）
        active_entities = self._get_active_entities(state)

        # 获取当前过滤器
        current_filters = state.current_filters.copy()

        # 检测是否是跟进查询
        is_follow_up = self._is_follow_up(state)

        return {
            'session_id': session_id,
            'is_follow_up': is_follow_up,
            'current_intent': state.current_intent.value if state.current_intent else None,
            'recent_queries': [q.original_query for q in recent_queries],
            'active_entities': active_entities,
            'current_filters': current_filters,
            'query_count': len(state.query_history),
            'session_duration': (datetime.now() - state.created_at).total_seconds() // 60,
        }

    def enhance_query(self, session_id: str, query: str) -> str:
        """
        使用上下文增强查询

        Args:
            session_id: 会话ID
            query: 原始查询

        Returns:
            增强后的查询
        """
        state = self.get_session(session_id)
        if not state:
            return query

        # 检测是否是跟进查询
        if not self._is_follow_up(state):
            return query

        # 获取缺失的上下文
        enhanced = query

        # 如果查询缺少时间范围但上下文有，继承时间范围
        if not self._has_time_reference(query) and 'time_range' in state.current_filters:
            time_range = state.current_filters['time_range']
            enhanced += f" (时间范围: {time_range})"

        # 如果查询缺少项目但上下文有，继承项目
        if not self._has_project_reference(query) and 'project' in state.current_filters:
            project = state.current_filters['project']
            if project not in query:
                enhanced += f" (项目: {project})"

        # 如果查询缺少AIDA但上下文有，继承AIDA
        if not self._has_aida_reference(query) and 'aida' in state.current_filters:
            aida = state.current_filters['aida']
            if aida not in query:
                enhanced += f" (AIDA: {aida})"

        return enhanced

    def get_suggestions(self, session_id: str) -> List[str]:
        """
        获取建议的后续查询

        Args:
            session_id: 会话ID

        Returns:
            建议列表
        """
        state = self.get_session(session_id)
        if not state or not state.query_history:
            return []

        suggestions = []
        last_query = state.query_history[-1]

        # 基于最后查询生成建议
        if last_query.intent == IntentType.QUERY:
            suggestions.extend([
                "这些缺陷的Matrix分布如何？",
                "按项目分组统计一下",
                "其中有多少是TopIssue？",
            ])
        elif last_query.intent == IntentType.ANALYSIS:
            suggestions.extend([
                "趋势如何？",
                "和上周对比有什么变化？",
                "风险最高的AIDA是哪些？",
            ])
        elif last_query.intent == IntentType.COMPARISON:
            suggestions.extend([
                "差异的主要原因是什么？",
                "哪个项目的风险更高？",
                "按严重级别细分一下",
            ])

        # 根据实体记忆个性化建议
        active_entities = self._get_active_entities(state)
        if 'project' in active_entities:
            project = active_entities['project']
            suggestions.append(f"{project}项目的长期缺陷有哪些？")

        return suggestions[:5]  # 最多返回5个建议

    def _analyze_intent(self, query: str, state: DialogueState) -> IntentType:
        """分析查询意图"""
        query_lower = query.lower()

        # 检测是否是新话题
        if any(word in query_lower for word in ['切换', '换一个', '新话题', '另外']):
            return IntentType.NEW_TOPIC

        # 检测是否是澄清请求
        if any(word in query_lower for word in ['什么意思', '解释一下', ' clarify']):
            return IntentType.CLARIFICATION

        # 检测是否是对比
        if any(word in query_lower for word in ['对比', '比较', 'vs', 'versus', 'difference']):
            return IntentType.COMPARISON

        # 检测是否是分析
        if any(word in query_lower for word in ['分析', '统计', '趋势', '为什么', '原因']):
            return IntentType.ANALYSIS

        # 检测是否是下钻
        if any(word in query_lower for word in ['详细', '明细', '具体', '详情']):
            return IntentType.DRILL_DOWN

        # 检测是否是跟进
        if self._is_follow_up(state) and any(word in query_lower for word in ['其中', '那', '还有', '呢']):
            return IntentType.FOLLOW_UP

        return IntentType.QUERY

    def _is_follow_up(self, state: DialogueState) -> bool:
        """检测是否是跟进查询"""
        if not state.query_history:
            return False

        last_query_time = state.query_history[-1].timestamp
        time_diff = (datetime.now() - last_query_time).total_seconds()

        # 5分钟内的查询视为跟进
        return time_diff < 300

    def _merge_entities(self, entities: List[Dict], state: DialogueState) -> List[Dict]:
        """合并实体（继承上下文）"""
        merged = entities.copy()

        # 如果是跟进查询，继承之前的实体
        if self._is_follow_up(state):
            current_types = {e.get('entity_type') for e in entities}

            for key, memory in state.entity_memory.items():
                # 只继承未过期的实体
                if memory.entity_type not in current_types:
                    time_since_last = (datetime.now() - memory.last_mentioned).total_seconds()
                    if time_since_last < 600:  # 10分钟内有效
                        merged.append({
                            'entity_type': memory.entity_type,
                            'value': memory.value,
                            'inherited': True,
                        })

        return merged

    def _update_entity_memory(self, state: DialogueState, entities: List[Dict]):
        """更新实体记忆"""
        now = datetime.now()

        for entity in entities:
            entity_type = entity.get('entity_type')
            value = entity.get('value')

            if not entity_type or value is None:
                continue

            key = f"{entity_type}:{value}"

            if key in state.entity_memory:
                # 更新现有记忆
                memory = state.entity_memory[key]
                memory.last_mentioned = now
                memory.mention_count += 1
            else:
                # 创建新记忆
                state.entity_memory[key] = EntityMemory(
                    entity_type=entity_type,
                    value=value,
                    confidence=entity.get('confidence', 1.0),
                    first_mentioned=now,
                    last_mentioned=now
                )

    def _get_active_entities(self, state: DialogueState) -> Dict[str, Any]:
        """获取活跃实体"""
        active = {}
        now = datetime.now()

        for key, memory in state.entity_memory.items():
            # 只返回最近提及的实体
            time_since = (now - memory.last_mentioned).total_seconds()
            if time_since < 600:  # 10分钟内
                active[memory.entity_type] = memory.value

        return active

    def _extract_filters(self, entities: List[Dict]) -> Dict[str, Any]:
        """从实体中提取过滤器"""
        filters = {}

        for entity in entities:
            entity_type = entity.get('entity_type')
            value = entity.get('value')

            if entity_type == 'time_range':
                filters['time_range'] = value
            elif entity_type == 'project':
                filters['project'] = value
            elif entity_type == 'severity':
                filters['severity'] = value
            elif entity_type == 'aida_domain':
                filters['aida'] = value
            elif entity_type == 'status':
                filters['status'] = value

        return filters

    def _has_time_reference(self, query: str) -> bool:
        """检查是否有时间引用"""
        time_patterns = [
            r'今天|昨天|本周|上周|本月|上月',
            r'最近|近\d+天|近\d+周|近\d+月',
            r'\d{4}-\d{2}-\d{2}',
            r'\d+月\d+日',
        ]
        return any(re.search(p, query) for p in time_patterns)

    def _has_project_reference(self, query: str) -> bool:
        """检查是否有项目引用"""
        project_patterns = [
            r'idcevo|idc|mgu|g70|g60|na6',
            r'项目',
        ]
        return any(re.search(p, query, re.IGNORECASE) for p in project_patterns)

    def _has_aida_reference(self, query: str) -> bool:
        """检查是否有AIDA引用"""
        aida_patterns = [
            r'aida|AIDA',
            r'音频|导航|媒体|adas|hmi|空调',
            r'模块|功能',
        ]
        return any(re.search(p, query, re.IGNORECASE) for p in aida_patterns)

    def _cleanup_if_needed(self):
        """清理过期会话"""
        current_time = time.time()

        if current_time - self._last_cleanup < self._cleanup_interval:
            return

        self._last_cleanup = current_time
        self.cleanup_expired_sessions()

    def cleanup_expired_sessions(self):
        """清理过期会话"""
        now = datetime.now()
        expired_sessions = []

        with self._lock:
            for session_id, state in self.sessions.items():
                inactive_time = (now - state.last_activity).total_seconds() / 60
                if inactive_time > self.SESSION_TIMEOUT:
                    expired_sessions.append(session_id)

            for session_id in expired_sessions:
                del self.sessions[session_id]

        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

    def get_session_stats(self) -> Dict[str, Any]:
        """获取会话统计"""
        with self._lock:
            total_sessions = len(self.sessions)
            total_queries = sum(len(s.query_history) for s in self.sessions.values())

            active_sessions = sum(
                1 for s in self.sessions.values()
                if (datetime.now() - s.last_activity).total_seconds() < 300
            )

        return {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'total_queries': total_queries,
            'avg_queries_per_session': total_queries / total_sessions if total_sessions > 0 else 0,
        }


# 便捷函数
_state_manager: Optional[DialogueStateManager] = None


def get_state_manager() -> DialogueStateManager:
    """获取全局状态管理器实例"""
    global _state_manager
    if _state_manager is None:
        _state_manager = DialogueStateManager()
    return _state_manager


def create_session() -> str:
    """创建新会话并返回会话ID"""
    manager = get_state_manager()
    state = manager.create_session()
    return state.session_id


def get_context(session_id: str) -> Dict[str, Any]:
    """获取会话上下文"""
    manager = get_state_manager()
    return manager.get_context(session_id)


def enhance_query(session_id: str, query: str) -> str:
    """使用上下文增强查询"""
    manager = get_state_manager()
    return manager.enhance_query(session_id, query)


def get_suggestions(session_id: str) -> List[str]:
    """获取建议"""
    manager = get_state_manager()
    return manager.get_suggestions(session_id)
