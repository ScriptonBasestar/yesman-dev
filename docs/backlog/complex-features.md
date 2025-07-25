# 복잡도가 높은 보류 기능들

## 높은 복잡도로 인한 보류 항목들

### IMPROVE-004: AI 기반 자동 문제 해결

**우선순위**: LOW **보류 사유**: 복잡한 AI 분석 엔진 및 Claude API 통합 필요

- 공통 이슈 패턴 감지 시스템
- 솔루션 제안 엔진 및 자동 실행 옵션
- Claude 연동 오류 보고 시스템
- 학습된 패턴 기반 예방적 조치 시스템

### IMPROVE-008: 코드 생성 자동화

**우선순위**: LOW **보류 사유**: 복잡한 코드 분석 및 생성 로직 필요

- TODO 항목 분석 및 코드 템플릿 매칭 시스템
- 프로젝트 패턴 학습 엔진
- API 엔드포인트, 테스트, 컴포넌트 템플릿 생성기
- 생성된 코드 검증 및 품질 체크

## 기술적 의존성이 높은 항목들

### 멀티 브랜치 작업 시나리오

**보류 사유**: 복잡한 git 워크플로우 관리 필요

- clone을 tmp디렉토리로 관리
- 격리된 디렉토리 지정 및 충돌 방지
- 브랜치별 독립적 작업 처리

### 수동 코드수정 순서 (권장 워크플로우)

**보류 사유**: 전체 워크플로우 재설계 필요

1. 공용 프롬프트 저장 및 관리 재사용
1. 코드수정 계획 - 수정코드를 파일로 삽입
1. 수정 실행 (수동 개발 + 자동실행)

### 프롬프트 자동실행 시스템

**보류 사유**: 복잡한 상태 관리 및 히스토리 시스템 필요

1. 선택 자동화 및 히스토리 audit 기록
1. 서브프로젝트 관리 (devbox → app subproject)
1. gitflow 방식 브랜치 관리

## 검증 및 정의가 필요한 항목들

### Add Validation for Template References

- 관련 ISSUE: Issue #4
- 보류 사유: 현재 대부분의 프로젝트가 "template: none"을 사용하고 있어 우선순위가 낮음

### Verify and Update Project Path Configuration

- 관련 ISSUE: Issue #8
- 보류 사유: 사용자와 정확한 프로젝트 구조 확인 필요

______________________________________________________________________

**검토 필요**: 모든 보류 항목은 실제 구현 전 상세 설계 검토 필요\
**업데이트**: 2025-07-07
