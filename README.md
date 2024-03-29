# PeerFinder (동료발견기)

- 4교육장 0주차 (2024.1.8(월) ~ 2024.1.11(목)) 미니 프로젝트
- Week00 7팀 - Lucky (김현우, 백강민, 여운관)

## 개발 기간

2024.01.08(월) 15:30 ~ 2024.01.11(목) 14:00

## 발표 자료

- [기획 발표 pdf](https://github.com/KraftonJungle4th/PeerFinder/files/13932248/default.pdf)
- [최종 발표 pdf](https://github.com/KraftonJungle4th/PeerFinder/files/13932253/516._7_._.2.pdf)

## 프로젝트 관리

- [Github Projects](https://github.com/orgs/KraftonJungle4th/projects/2)

## 기획 의도

- 매주 팀이 바뀌는 정글 분만 아니라 앞으로 수많은 자기소개를 해야 할 정글러 분들을 위해 기획했습니다.
- 자기소개를 간단하게 하고, 상대방의 정보를 빠르게 파악해서 낯선 환경에서 소개나 파악의 어려움을 해결하고자 했습니다.

## 주요 기능

### 구현 완료

- 로그인/회원가입
- JWT
- Jinja2 (SSR)
- 프로필 등록
- 프로필 게시
- 프로필 QR코드 기능

### 미구현

> 기획은 했으나, 시간 상의 이유로 구현되지 않은 기능

- 로그아웃
- 프로필 삭제
- 좋아요 기능
- 좋아요 몰아보기

## 기술 스택

- 웹 프론트엔드: Bootstrap
- 웹 백엔드: Flask, Jinja2, JWT
- 데이터베이스: MongoDB

## 배포

- Server: Amazon EC2 SERVICE Ubuntu 18.04
- DB: MongoDB Atlas

## 기술적 챌린지

### 1. [JWT](./docs/JWT.md)

- 개념 이해와 기존 로그인을 JWT로 변경

### 2. [Jinja2](./docs/Jinja2.md)

- SSR 개념 이해 및 적용

## 개발 일정

1. 2024.01.08(월) : 기획, 발표 준비
2. 2024.01.09(화) : 로그인, 회원가입, 페이지 CSS 구현, github 관리
3. 2024.01.10(수) : JWT, Jinja2 구현
4. 2024.01.11(목) : 사용자 등록, 게시 구현 , 최종 발표

## 역할 분배

- 김현우: 기획, Github 환경 구축, 프로필 QR 코드 제공 기능 구현, EC2 업로드 및 배포 관리
  - EC2 업로드 및 배포 관리: FileZila 및 Putty 접속 후 nohup 명령어 이용
- 백강민: 로그인, 회원가입, 내 프로필 관리, 프로필 보여주기 구현, 기획 및 최종 발표자
  - 로그인: JWT 적용
  - 회원가입: Jinja2 적용
- 여운관: 회원가입, 로그인, 내 프로필, 내 좋아요 회원 목록 화면 구현
  - 내 좋아요 화면: Bulma 이용
