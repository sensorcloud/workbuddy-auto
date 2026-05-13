"""
市场服务层
提供资产搜索、详情、评价等功能
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
import json

from app.models.asset import Asset
from app.models.order import Order


class MarketplaceService:
    """市场服务类"""

    @staticmethod
    def search_assets(
        db: Session,
        filters: dict = None,
        page: int = 1,
        page_size: int = 20,
        sort: str = "created_desc",
    ) -> dict:
        """
        基于Asset表的SQL查询 + 多条件筛选 + 排序 + 分页。

        filters 支持:
        - gpu_model: 筛选 spec JSON 中的 gpu 字段
        - gpu_count: 筛选 spec JSON 中的 gpu_count 字段
        - vram_min: 筛选 spec JSON 中的 vram_total >= vram_min
        - region: 筛选 location JSON 中的 region 字段
        - min_price / max_price: 筛选 pricing JSON 中的 unit_price
        - green_ratio_min: 筛选 energy_profile JSON 中的 green_ratio
        - pue_max: 筛选 energy_profile JSON 中的 PUE
        - pricing_type: 筛选 Asset.pricing_type
        - status: 筛选 Asset.status（默认 "online"）

        sort 支持: price_asc, price_desc, rating_desc, created_desc

        返回 {"items": [...], "total": int, "page": int, "page_size": int, "filters_applied": {...}}
        """
        if filters is None:
            filters = {}

        # 默认只查在线资产
        query = db.query(Asset).filter(Asset.status == filters.get("status", "online"))

        filters_applied = {}

        # 筛选 gpu_model
        gpu_model = filters.get("gpu_model")
        if gpu_model:
            # JSON 字段模糊匹配
            query = query.filter(
                or_(
                    Asset.spec.is_(None),
                    Asset.spec.like(f'%"gpu":%{gpu_model}%'),
                )
            )
            filters_applied["gpu_model"] = gpu_model

        # 筛选 region
        region = filters.get("region")
        if region:
            query = query.filter(
                or_(
                    Asset.location.is_(None),
                    Asset.location.like(f'%"region":"{region}"%'),
                )
            )
            filters_applied["region"] = region

        # 筛选 pricing_type
        pricing_type = filters.get("pricing_type")
        if pricing_type:
            query = query.filter(Asset.pricing_type == pricing_type)
            filters_applied["pricing_type"] = pricing_type

        # 获取所有结果后在 Python 层过滤（简化实现）
        # 性能优化方案（如果数据量小 <1000）：Python 层过滤 + 排序 + 分页即可
        all_assets = query.all()

        # Python 层精细过滤
        filtered_assets = []
        for asset in all_assets:
            # gpu_count 筛选
            gpu_count = filters.get("gpu_count")
            if gpu_count:
                spec_gpu_count = asset.spec.get("gpu_count") if asset.spec else None
                if spec_gpu_count is None or int(spec_gpu_count) != int(gpu_count):
                    continue

            # vram_min 筛选
            vram_min = filters.get("vram_min")
            if vram_min:
                vram_total = asset.spec.get("vram_total") if asset.spec else 0
                if vram_total < vram_min:
                    continue

            # min_price / max_price 筛选
            min_price = filters.get("min_price")
            max_price = filters.get("max_price")
            if min_price is not None or max_price is not None:
                unit_price = (
                    asset.pricing.get("unit_price")
                    if asset.pricing and "unit_price" in asset.pricing
                    else None
                )
                if unit_price is None:
                    unit_price = (
                        asset.pricing.get("compute_price_per_hour")
                        if asset.pricing
                        else 0
                    )
                if min_price is not None and unit_price < min_price:
                    continue
                if max_price is not None and unit_price > max_price:
                    continue

            # green_ratio_min 筛选
            green_ratio_min = filters.get("green_ratio_min")
            if green_ratio_min:
                green_ratio = (
                    asset.energy_profile.get("green_ratio")
                    if asset.energy_profile
                    else 0
                )
                if green_ratio < green_ratio_min:
                    continue

            # pue_max 筛选
            pue_max = filters.get("pue_max")
            if pue_max:
                pue = (
                    asset.energy_profile.get("PUE")
                    if asset.energy_profile
                    else 999
                )
                if pue > pue_max:
                    continue

            filtered_assets.append(asset)

        # 排序
        if sort == "price_asc":
            filtered_assets.sort(
                key=lambda a: (
                    a.pricing.get("unit_price", float("inf"))
                    if a.pricing
                    else float("inf")
                )
            )
        elif sort == "price_desc":
            filtered_assets.sort(
                key=lambda a: (
                    a.pricing.get("unit_price", 0)
                    if a.pricing
                    else 0
                ),
                reverse=True,
            )
        elif sort == "rating_desc":
            filtered_assets.sort(key=lambda a: a.rating or 0, reverse=True)
        else:  # created_desc
            filtered_assets.sort(key=lambda a: a.created_at or "", reverse=True)

        # 分页
        total = len(filtered_assets)
        offset = (page - 1) * page_size
        paginated_assets = filtered_assets[offset : offset + page_size]

        return {
            "items": paginated_assets,
            "total": total,
            "page": page,
            "page_size": page_size,
            "filters_applied": filters_applied,
        }

    @staticmethod
    def get_asset_detail(db: Session, asset_id: str) -> dict:
        """
        获取资源详情。聚合评价信息：
        - Asset 基本信息
        - spec, pricing, energy_profile, location
        - availability_sla, rating, total_orders, pricing_type
        - reviews: 从 Order 表中查询 asset_id 对应且有 review_score 的订单
        """
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            return None

        # 查询评价
        reviews_query = (
            db.query(Order)
            .filter(
                Order.asset_id == asset_id,
                Order.review_score.isnot(None),
            )
            .order_by(Order.reviewed_at.desc())
            .limit(10)
            .all()
        )

        reviews = []
        for order in reviews_query:
            reviews.append(
                {
                    "order_id": order.id,
                    "user_id": order.user_id,
                    "score": order.review_score,
                    "text": order.review_text,
                    "reviewed_at": (
                        order.reviewed_at.isoformat() if order.reviewed_at else None
                    ),
                }
            )

        return {
            "id": asset.id,
            "owner_id": asset.owner_id,
            "type": asset.type,
            "status": asset.status,
            "spec": asset.spec,
            "pricing": asset.pricing,
            "energy_profile": asset.energy_profile,
            "location": asset.location,
            "availability_sla": asset.availability_sla,
            "rating": asset.rating,
            "total_orders": asset.total_orders,
            "pricing_type": asset.pricing_type,
            "created_at": asset.created_at.isoformat() if asset.created_at else None,
            "updated_at": asset.updated_at.isoformat() if asset.updated_at else None,
            "reviews": reviews,
            "review_count": len(reviews),
        }

    @staticmethod
    def get_reviews(
        db: Session,
        asset_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        获取资源评价列表。
        从 Order 表中查询 asset_id 对应且有 review_score 的订单。
        返回 {"items": [...], "total": int, "page": int, "page_size": int}
        """
        query = db.query(Order).filter(
            Order.asset_id == asset_id,
            Order.review_score.isnot(None),
        ).order_by(Order.reviewed_at.desc())

        total = query.count()
        offset = (page - 1) * page_size
        orders = query.offset(offset).limit(page_size).all()

        items = []
        for order in orders:
            items.append({
                "order_id": order.id,
                "user_id": order.user_id,
                "score": order.review_score,
                "text": order.review_text,
                "reviewed_at": order.reviewed_at.isoformat() if order.reviewed_at else None,
            })

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    def create_review(
        db: Session,
        asset_id: str,
        order_id: str,
        user_id: str,
        score: int,
        text: str = None,
    ) -> dict:
        """
        创建资源评价。
        - 写入 Order.review_score, review_text, reviewed_at
        - 更新 Asset.rating (平均分), Asset.total_orders += 1
        """
        from datetime import datetime

        # 验证订单
        order = (
            db.query(Order)
            .filter(
                Order.id == order_id,
                Order.asset_id == asset_id,
                Order.user_id == user_id,
            )
            .first()
        )
        if not order:
            raise ValueError("订单不存在或无权评价此订单")

        if order.status != "completed":
            raise ValueError("只能评价已完成的订单")

        if order.review_score is not None:
            raise ValueError("此订单已评价")

        # 验证评分
        if score < 1 or score > 5:
            raise ValueError("评分必须在 1-5 之间")

        # 更新订单评价
        order.review_score = score
        order.review_text = text
        order.reviewed_at = datetime.utcnow()

        # 更新资产评分
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if asset:
            # 计算新的平均评分
            all_reviews = (
                db.query(Order)
                .filter(
                    Order.asset_id == asset_id,
                    Order.review_score.isnot(None),
                )
                .all()
            )
            total_score = sum(r.review_score for r in all_reviews) + score
            review_count = len(all_reviews) + 1
            new_rating = total_score / review_count

            asset.rating = round(new_rating, 2)
            asset.total_orders = (asset.total_orders or 0) + 1

        db.commit()
        db.refresh(order)

        return {
            "success": True,
            "order_id": order_id,
            "score": score,
            "text": text,
            "reviewed_at": order.reviewed_at.isoformat(),
        }
